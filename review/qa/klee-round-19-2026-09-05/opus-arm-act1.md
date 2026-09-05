# Blind seat — KLEEMOD-KLEE, lane 1, round 19 (targeted)

## Identity

- **Model / seat:** Opus, blind TESTER seat, lane 1.
- **Run seed:** `BTJFUT7XQSQX`. **Ascension:** 0. **Character:** Klee.
- **Act:** 1. The map named the act boss **Waterfall Giant** (never reached).
- **Actions accepted:** 112 of 120.
- **Termination:** stopped voluntarily at 112 with 8 acts left, at a map
  boundary after the treasure room on floor ~10. 8 acts cannot open and finish
  a fight; the alternative was being cut off mid-combat by `budget reached`,
  which would have produced a half-fight with no decisions to report. The boss
  was 7 floors further on and was never in reach at this cap. No wall-clock or
  refusal stop; **zero refused commands and zero stalls all round.**
- **HP trajectory:** 62 → 58 (fight 1) → 52 (fight 2) → 41 (elite t2) → **15**
  (elite t5, the one dangerous turn) → 15 (fight 4, took zero damage) → **33/62**
  after the rest site.
- **Gold:** 146. **Potions:** Attack Potion, Weak Potion (never used either).
- **Relics:** Pounding Surprise (start), Scroll Boxes (Neow), Nunchaku (elite),
  Rainbow Ring (treasure).
- **Deck at the end:** Ammo Scavenging, Barbara — Front Row Seat, Careful
  Arrangement, Catalytic Converter, Chain Fuse, Defend ×4 (one enchanted
  *Spiral*), Fireworks Show, Fwoosh!+, Grounded, Jumpy Dumpty, Ka-pow!, Mine
  Toss, Pocket Match ×2, Pop!+, Rapid Fire, Run Away!, Strike ×4, Tinder Toss.

**Neow pick: Scroll Boxes**, then **bundle 1** (Mine Toss / Run Away! /
Catalytic Converter). Scroll Boxes because it was the only option of the three
that printed card faces and asked me to choose between them — the other two
hand you something unseen, and I am here to read. Bundle 1 over bundle 2
because bundle 2 was three *detonators* (and duplicated a Tinder Toss I already
held) while my relic, Pounding Surprise, pays only "whenever a Bomb goes off":
without a Bomb *source* the whole bundle would have been inert, and Mine Toss
was the only printed card on the screen that made Bombs.

---

## Fight 1 — Sludge Spinner [A], 38 HP

**The finding of this fight is turns 1 and 2, not turn 3.** I opened holding
three cards that set off Bombs and one that grows them, and **no card that
makes a Bomb.** Chain Fuse ("Each Bomb on the enemy grows by 6") and every
*Set off* had literally nothing to act on.

- **T1.** Tinder Toss → Strike → Ka-pow! → Defend. 18 damage, 5 Block.
  *Rejected:* Chain Fuse, because there were no Bombs for it to grow — not a
  choice, an exclusion. The one thing I actually learned was worth the turn:
  Tinder Toss dealt 8 and **Energy stayed 3/3**, so the printed line "its 1
  Spark is a price, not an Energy cost" is exactly true.
- **T2.** Strike, Strike, Defend. *Rejected:* Catalytic Converter and Careful
  Arrangement — both inert. The screen itself said so, in caps: "NO REACTION IS
  REACHABLE HERE." **A turn with no rejected alternative: my hand held five
  cards and three of them could not legally do anything useful.**
- **T3.** Pop! (Bomb 5) → Jumpy Dumpty (Bomb 8) → Rapid Fire. The enemy read
  **"Bomb 13 — Set off here deals 13 Pyro damage, in 2 hits for as many Sparks.
  Bombs here: 5 / 8"**, which is the clearest status line I have seen in any of
  these runs. Rapid Fire alone (12) was exact lethal on 12 HP; I deliberately
  spent the extra cards to watch the chain resolve, since the fight ended
  either way. *Rejected:* the one-card lethal — I traded a tidy kill for
  information.

| turn | Sparks (end) | anything went off | Grounded paid |
|---|---|---|---|
| 1 | 0 | no | not drawn |
| 2 | 0 | no | not drawn |
| 3 | (combat ended) | **yes** — 2 Bombs | not drawn |

**Tinder Toss / Rapid Fire log.** T1 Tinder Toss → Sludge Spinner [A], **no
Bomb** (8 raw). T3 Rapid Fire → Sludge Spinner [A], **carried Bomb 13** (set
off). With one enemy the "random" targeting never had a decision to make.

**Companion offered:** Barbara — Front Row Seat. **Taken.** She was the only
Hydro on the screen and my deck is monochrome Pyro; the Elemental Reaction
block is a large chunk of the rules text and without her not one word of it
could ever fire.

---

## Fight 2 — Corpse Slug (1) [A] 26 HP, Corpse Slug (2) [B] 27 HP

Both carried **Ravenous 4**: "When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength." That single line made the whole
fight a decision about *sequencing a kill*, which is the best thing that
happened in the round.

- **T1.** Mine Toss (Mine 4 on both) → Jumpy Dumpty **on A** → Strike B.
  *The decision, and it was made here:* where to put the Bomb 8. Mines "also go
  off before its enemy's hit", so a Mine on the body that is *attacking* spends
  itself for chip damage, while a Mine on the body that is *not* attacking sits
  and compounds. B was attacking and A was debuffing, so I put the payload on A
  and let B's Mine chip B for free. *Rejected:* Bomb 8 on B, which would have
  fed the payload to a self-trigger.
- **T2.** Ka-pow! on A → Strike A (kill) → Pop! on B → Grounded → Defend.
  Ka-pow! set off **Bomb 20** for 24 total, leaving A at 2. *Rejected:* letting
  A's own Mine finish it on the enemy turn. I paid a Strike to kill A **inside
  my turn** specifically so B's Ravenous Stun would land before B could act —
  and it did: **I took 0 damage that enemy turn.** Jumpy Dumpty's rider also
  fired here, seeding a Mine 3 on *both* bodies.
- **T3.** Chain Fuse on B → Strike → Run Away! → Defend. A's Mine had migrated
  on the kill ("A kill moves them to a survivor"), so B read **"Bombs here: 7 /
  7 / 9, including 2 Mines."** Those two Mines self-detonate before B's hit; at
  7+7=14 they leave B alive at 3 and I eat 12, but Chain Fuse pushed them to
  13+13=26 against 17 HP, so **the Mines killed B before its swing landed** —
  "which lands in full unless the Mine kills." *Rejected:* **Careful
  Arrangement**, which would have merged the three Bombs into one. That would
  have collapsed 3 growth-ticks into 1 and, I suspected, converted the two
  Mines into a plain Bomb, destroying the exact property that won the turn.

| turn | Sparks (end) | anything went off | Grounded paid |
|---|---|---|---|
| 1 | 1 | yes — B's Mine 4, on the enemy turn | not played yet |
| 2 | 4 | **yes** — 2 Bombs (Ka-pow!) | played this turn (pays from next) |
| 3 | 5 | **yes** — 2 Mines, which killed B | **yes** — 6 Block + 1 Spark |

**Companion offered:** Gorou — General's War Banner ("gain 2 Dexterity for 2
turns, then the banner takes 2 back"). **Not taken** — the Dexterity is lent,
not given. Took Fwoosh! instead, because fight 2 ended with me holding **5
Sparks and no card that could spend them.**

---

## Fight 3 (ELITE) — Terror Eel [A], 140 HP

**Shriek 70:** "The first time Terror Eel's HP reaches 70 or below, it becomes
Stunned." This is the fight the kit is built for, and it is the best fight of
the round.

- **T1.** Jumpy Dumpty (Bomb 8) → Barbara (5 Block, Hydro) → Strike. Took 11.
  *Rejected:* two Strikes for 12 damage, which would have cost me 5 more HP and
  laid no Hydro. Note the reasoning I was making at the draft, not the turn:
  **separate Bombs each grow 4 a turn, so more Bombs means faster growth** —
  which is precisely why Careful Arrangement is a trap.
- **T2.** Fwoosh!+ → Ammo Scavenging → Run Away! → Mine Toss → Defend, **in
  that order, and the order was the decision.** Fwoosh!+ printed a live
  *"Reaction preview: Vaporize — Pyro meets Hydro: this hit deals 1.5x damage"*.
  The Hydro aura had 1 turn left, so the window was now. 12 Vaporized to 18,
  plus 9 = **27 exactly as previewed** (134 → 107). Detonating *first* then
  turned on Run Away!'s conditional (+4, "if a Bomb went off this turn") and
  Ammo Scavenging's draw. *Rejected:* banking the Bomb another turn — I worked
  out that Vaporize is worth only 0.5 × the **oldest** Bomb (the first hit takes
  the aura), so +6 now versus +4/turn growth, and the aura's expiry broke the
  tie.
- **T3.** Pop!+ → Chain Fuse → Ka-pow! → Rapid Fire. **The turn of the round.**
  The Eel sat at 100 and Shriek was 30 away: Pop!+ made a second Bomb, Chain
  Fuse grew both by 6 (to 27), Ka-pow! set off 27+4=31 → **69, Shriek fired,
  "Intent: Stunned"**, and its telegraphed 22 never landed. *Rejected:* Defend
  Spiral for 10 Block — once the Stun was reachable, Block was strictly worse
  than the damage that made the Stun happen. I then spent the last 2 Energy on
  Rapid Fire rather than Block, precisely *because* the enemy could not act.
- **T4.** Grounded → Tinder Toss → Strike → Defend. Only a debuff incoming.
  Grounded went down on a board with **no Bomb on it**, so it paid nothing;
  I played it as an investment. *Rejected:* Catalytic Converter — see (b).
- **T5. The one bad turn, and the tightest decision.** I was **Vulnerable 99**
  and the Eel telegraphed **33** (its 22 already multiplied). I played Mine Toss
  → Pocket Match (set off the Mine) → **Pop!+ afterwards** → Strike → Run Away!.
  The ordering is the whole point: Run Away!'s +4 requires a Bomb to go off
  *during my turn*, but Grounded requires a Bomb still standing *at the start of
  the next one*. Detonating the Mine bought the Block; placing Pop!+'s Bomb
  **after** the set-off left something on the field for Grounded. *Rejected:*
  holding Pocket Match (Retain) and just blocking — I costed it out and it left
  me at 11 HP with the Eel at 33 instead of 15 HP with the Eel at 28. Took 26,
  down to 15.
- **T6.** Jumpy Dumpty → Rapid Fire. **This is the plan paying off, not a dead
  turn:** the Bomb planted on T5 had grown to 11, Grounded's 6 Block had kept me
  alive, and adding a second Bomb *before* the Set off made it 19 + Rapid Fire's
  12 = 31 into 28 HP. The obvious lethal was set up two turns earlier.

| turn | Sparks (end) | anything went off | Grounded paid |
|---|---|---|---|
| 1 | 2 | no | not played yet |
| 2 | 2 | **yes** — 1 Bomb (Vaporize) | not played yet |
| 3 | 6 | **yes** — 2 Bombs → Shriek Stun | not played yet |
| 4 | 5 | no | **no** — played this turn, no Bomb on field |
| 5 | 5 | **yes** — 1 Mine | **no** — no Bomb had survived T3 |
| 6 | (combat ended) | **yes** — 2 Bombs | **yes** — 6 Block + 1 Spark |

**Tinder Toss / Rapid Fire log.** T3 Rapid Fire → Terror Eel [A], **no Bomb**
(Ka-pow! had already emptied the body earlier that turn) — 12 raw. T4 Tinder
Toss → Terror Eel [A], **no Bomb** — 8 raw. T6 Rapid Fire → Terror Eel [A],
**carried Bombs 11 + 8 = 19** — lethal.

**Companion offered:** Sucrose — Catalyst Conversion. **Not taken**; took
Fireworks Show, again to buy a sink for surplus Sparks.

---

## Fight 4 — Toadpole (1) [A] 24 HP, Toadpole (2) [B] 21 HP

Entered at **15/62**. Won it taking **zero damage**, which is the clearest
evidence the engine had come online.

- **T1.** Ammo Scavenging on B → Barbara on B → Defend. 10 Block against 7.
  *The decision:* **both my detonators (Ka-pow!, Pocket Match) print Retain**,
  so I could bank them, plant, and pop later. *Rejected:* setting off a Bomb 4
  immediately for small change. I put Barbara's Hydro on the same body as the
  Bomb so the Vaporize would land where the payload was.
- **T2.** Pop!+ on B → Ka-pow! on B → Jumpy Dumpty on A → Grounded → Defend
  Spiral. Set off 8 (Vaporized to 12) + 7 + 4 = 23 into 21 HP; **B died.**
  A had grown **Thorns 2** ("When hit by an attack, deal 2 damage back... a
  Skill's too"), which at 15 HP made attacking it genuinely costly — so I
  routed all damage through Bombs, which the glossary states are "Not an
  Attack." *Rejected:* Strike on A, for exactly that reason.
- **T3.** Mine Toss → Fwoosh!+. Grounded paid, the Bomb had grown to 12, Mine
  Toss made it 16, Fwoosh!+ set off 16 + 9 = 25 into 24 HP. Lethal for one
  Energy and one Spark. *Rejected:* Fireworks Show / Pocket Match / Strike —
  three redundant routes to the same kill, which is a pleasant problem.

| turn | Sparks (end) | anything went off | Grounded paid |
|---|---|---|---|
| 1 | 2 | no | not played yet |
| 2 | 4 | **yes** — 2 Bombs (Vaporize killed B) | played this turn |
| 3 | (combat ended) | **yes** — 2 Bombs | **yes** — 6 Block + 1 Spark |

**Companion offered:** Gorou — Inuzaka All-Round Defense. **Not taken**; took a
second Pocket Match for reliability at 15 HP.

---

## The six targeted cards

- **Pop!** — played 4×, in every fight. Core. A 0-cost Bomb is the card that
  makes every other card in the deck legal.
- **Chain Fuse** — played 2×, and **both were decisive** (killed B through its
  own Mines in fight 2; set up the Shriek Stun in the elite). Best of the six.
- **Grounded** — played 3×, **paid 3 times and failed to pay twice**, and the
  two failures taught me the most (see (c)).
- **Rapid Fire** — played 3×: twice into a body carrying Bombs (both lethal),
  once into a bare body for 12 raw. Fine, but 2 Energy competes with Block.
- **Tinder Toss** — played 2×, and **both times the body carried no Bomb**, so
  it was 8 raw damage twice. Never once did I get to use it as a detonator.
- **Careful Arrangement** — **never played, never wanted, drawn 3 times.** See
  (b) and (d).

---

## The kit, after 4 fights

**(a) Which decisions felt like real choices, and where they were made.**

The best ones were *sequencing* decisions inside a turn, and there were several
genuinely difficult ones:

1. **Elite T5 — Run Away! versus Grounded, made on the turn.** Run Away!'s +4
   needs a Bomb to go off *this turn*; Grounded's 6 Block needs a Bomb *still
   standing next turn*. Those two cards pull in opposite directions and the
   resolution was to detonate a Mine and *then* place a fresh Bomb. That is a
   real, non-obvious, card-text-driven decision and it was the highlight.
2. **Fight 2 T2 — killing A inside my turn rather than letting its Mine do it,
   made on the turn.** Ravenous meant the *timing* of a kill decided whether I
   ate 8 damage. Paying a Strike to control that timing was a trade I could see
   and price.
3. **Fight 2 T1 — which body gets the payload, made on the turn.** Mines
   self-spend on attackers, so the target choice was between free chip damage
   and a compounding charge. Genuinely two-sided.
4. **Elite T3 — burst to the Shriek threshold instead of blocking.** A visible
   number (70) converted damage into damage-prevention. Excellent.
5. **At the draft:** taking bundle 1 over bundle 2 (fuel over detonators, read
   off the relic), and taking **Barbara**, which is what made the entire
   Elemental Reaction ruleset reachable. The elite's T2 Vaporize was won at a
   card-reward screen two floors earlier.

The trade being made is nearly always **now versus later**: Bombs grow 4 a turn
for free, so every detonation is cashing an appreciating asset early, and every
turn spent blocking is offense. That is a good spine.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** Filler. Fight 1 turn 2 was literally Strike, Strike,
  Defend with no alternative.
- **Careful Arrangement** — *never worth playing, in any board state I saw.*
  Merging N Bombs into 1 destroys N-1 growth ticks a turn, collapses a
  multi-hit Set off (fewer Sparks — the readout says "in 2 hits for as many
  Sparks"), and I believe converts Mines into a plain Bomb, losing the
  auto-trigger. Its +5 does not come close to covering that. I would cut it.
- **Catalytic Converter** — dead on arrival. It makes Sparks conditional on
  Elemental Reactions, and I had exactly one Hydro source in the whole deck.
  It is a card that generates surplus of a resource I already could not spend.
- **The end of every fight** was automatic in a good way (see the (a) note about
  plans paying off), but **fights 1 and 2 opened with genuinely dead turns.**

**(c) What I could not understand, or that contradicted its printed text.**

- **Nothing contradicted its text.** Every number I predicted landed exactly:
  27 from the previewed Vaporize, 31 to hit the Shriek line, 25 into 24 HP.
  The Bomb status line ("Bombs here: 7 / 7 / 9, including 2 Mines") is the best
  piece of writing in the kit and I made three plans directly off it.
- **The one real trap: Grounded's condition is invisible until it silently
  fails.** It reads "if you have a Bomb on the field" — but detonating is how
  you *empty* the field, so the power turns itself off exactly when you use the
  engine. It failed to pay twice (elite T4 and T5) and **the screen gave no
  indication of the near-miss** — no "Grounded did not trigger" line, just an
  absent 6 Block I had to notice by diffing my own Block total. That is a
  legibility gap, not a rules bug.
- **Thorns 2 versus Bombs was genuinely ambiguous.** Thorns says "Every card hit
  is one, a Skill's too", while Bomb says "Not an Attack". I could not tell from
  the screens whether a Bomb going off would reflect 2 damage back at me, and at
  15 HP I did not dare find out. I routed around it rather than learn it.
- **The Doors of Light and Dark event never printed which 2 cards it upgraded.**
  I only discovered Fwoosh!+ and Pop!+ by drawing them a fight later.
- **Minor:** "Vulnerable 99" and "Shriek 70" both use a number that is not a
  stack count, which read oddly beside real stack counts like Frail 2.

**(d) The card I never wanted, and the one I was happiest to draw.**

- **Never wanted: Careful Arrangement.** Drawn three times, played zero, and
  each time it was actively the *wrong* card — its effect makes the engine
  worse, not merely nothing. That is worse than a blank.
- **Happiest to draw: Pocket Match** (bought for 25 gold — the buy of the act).
  *Retain* plus a Spark price means it is never dead, never competes for
  Energy, and it solves the kit's actual failure mode. Honourable mention to
  **Chain Fuse**, which won two fights outright.

**(e) Did the first turn of the first fight already present a decision?**

**Not really — and this is the round's sharpest finding.** I opened with
Ka-pow!, Tinder Toss and Chain Fuse — three cards that all reference Bombs —
and **no card that creates one.** Chain Fuse was strictly inert. The "decision"
reduced to playing my whole hand in the only order that worked, and I would
have played the same four cards on autopilot. The kit did not become
interesting until **fight 1 turn 3**, the first time I held a Bomb source and a
detonator simultaneously; from there it was consistently good. The opening hand
of the starting deck is carrying real risk of teaching a new player that half
their cards do nothing.

One structural note across all four fights: **Spark generation badly outruns
Spark sinks.** I ended fights holding 5, 6, and 5 Sparks with no card in hand
that could spend them, and Sparks are "Gone after combat." Both my card-reward
picks after fight 2 and after the elite (Fwoosh!, Fireworks Show) were spent
buying sinks for a resource the relic hands me automatically. Pounding Surprise
plus multi-hit Set offs produce Sparks far faster than the ~1-per-turn a deck
can consume, and Catalytic Converter proposes to make *more*.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, `GITS_LANE=1 python -m
understudy.blindplay observe` and `... act "<command>"`, run through the Bash
tool. I never used `GITS_LANE=2`, and I ran no other understudy subcommand —
no `harness state`, `scenario`, `staged_turn`, or `soak`.

Other tool calls, in full:

- **Bash, `mkdir -p ...scratchpad\klee19`** — created a scratch directory at the
  start. I never wrote anything into it; all notes were kept in my head.
- **Bash, `mkdir -p review\qa\klee-round-19-2026-09-05`** — created the record
  directory named by the coordinator.
- **Bash, `... observe 2>&1 | sed -n '<ranges>'`** — many times, to re-read one
  block (usually the enemy panel or my hand) of an `observe` I had already
  taken, to avoid re-printing the full screen. `sed` only ever filtered the
  output of an allowed `observe`; it never read a file.
- **Write tool, once** — this record.

No refused commands and no stalls occurred at any point in the round, so there
is nothing to report under those headings.

Caveat on the stop: I ended at 112 accepted acts rather than running to the
120 cap, by my own judgement, for the reason given under Identity.
