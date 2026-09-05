# Klee — round 17, lane 2, blind natural run, Act 1

## Identity

- **Model / seat:** Opus, blind TESTER seat, lane 2 (`GITS_LANE=2`).
- **Run seed:** `TSRRAR5Q4U3K`. **Ascension:** 1. **Character:** Klee (KLEEMOD-KLEE).
- **Act:** 1. The map named the act boss **Lagavulin Matriarch**. Never reached it.
- **Actions accepted:** 114 of 120.
- **Termination:** action budget. At 114 the only node forward was an Elite, I was
  at 9/62 HP, and 6 actions cannot finish an elite fight. Stopped rather than walk
  into it to make the log tidier. Wall clock was nowhere near 5400 s. No refusal
  streak, no stall — every command I sent was accepted.
- **HP trajectory:** 62 → 51 (fight 1) → 50 (fight 2) → 42 (event, −8 HP by
  choice) → 40 (fight 3) → **19** (elite) → 9 (fight 5). Ended **9/62**.
- **Gold:** 195 by my own arithmetic (99 after Neow, +19 +13 +11 +37 +16 from
  printed rewards). The last figure the map actually printed to me was 118.
- **Potions held at the end:** Gambler's Brew (1 of 3 slots). Spent Ghost in a Jar
  and Cunning Potion in fight 5.
- **Relics:** Pounding Surprise, Scroll Boxes, Strike Dummy.
- **Deck at the end** — the floor-8 snapshot the map printed, plus what I picked
  after it: Big Badda Boom, Defend ×4, Dig In, Dodoco Cover, Fish-Flavored Bait,
  Fwoosh!, Jumpy Dumpty, Ka-pow!, Mine Toss, Rapid Fire, Run Away!, Strike ×4,
  **Albedo — Solar Isotoma**, **Quick Fuse**. (That snapshot also listed
  `Shiv+ ×3`, which were Cunning Potion tokens, and omitted Albedo, which was in
  play as a power. The screen prints a caveat saying it is the last fight's deck.)

**Neow pick:** *Scroll Boxes* — "Choose 1 of 2 packs of cards to add to your Deck."
Of the three offers it was the only one that handed me a decision rather than a
random result, and at 62/62 on A1 I was not paying 12 Max HP for two random
transforms.

**The bundle I chose, and why:** bundle 2 (Dodoco Cover / Run Away! / Rapid Fire)
over bundle 1 (Sorry, Jean… / Pocket Match / Bang Bang!). Bundle 1's two attackers
were Spark-priced, the Spark screen said "Start each combat with 1", and the relic
that makes more Sparks — Pounding Surprise — only pays "Whenever a Bomb goes off".
Bundle 1 had no cheap way to put a Bomb down, so **Bang Bang! at 2 Sparks is
uncastable on turn 1 of a fight and stays uncastable until something else places
and pops a Bomb.** Bundle 2 was energy-priced and self-starting. This was the
single most load-bearing decision of the act.

---

## Fight 1 — Sludge Spinner 38/38

**Turn 1** (62 HP, 3 energy). Hand: Strike ×4, Run Away!. Played Strike, Strike,
Strike (18) and Run Away! (3 Block).
*Alternative rejected:* none that existed. The only question was which three of
four identical Strikes, and Run Away! is 0 cost so holding it bought nothing —
its rider ("+4 additional Block if a Bomb went off this turn") cannot turn on when
no card in hand places a Bomb. **This turn presented no decision.** Took 5.

**Turn 2** (57 HP, Weak 1). Hand: Defend ×3, Ka-pow!, Rapid Fire. Played Rapid
Fire (printed **"deal 2 damage to it, 4 times"** — base 3, live-adjusted for Weak)
and one Defend.
*Alternative rejected:* playing Ka-pow! now. It printed 3 damage under Weak and 4
without, and it has Retain, so holding it was a free +1. Also rejected three
Defends, which would have stalled a fight I was winning. Small decision, real one.

**Turn 3** (51 HP, enemy 12). Hand: Ka-pow!, Defend ×3, **Jumpy Dumpty**,
**Dodoco Cover**. Played Dodoco Cover (Bomb 4, 5 Block) and Jumpy Dumpty (Bomb 8).
The enemy panel then read exactly:

> **Bomb 12 (buff)** — Set off here deals 12 Pyro damage. Bombs here: 4 / 8,
> growing each turn. None goes off by itself.

Ka-pow! set off for 12 and hit for 4. 16 into 12 HP. Kill.
*Alternative rejected:* Ka-pow! plus three Defends — 4 damage and a wasted turn
against an enemy about to buff. **This was the first turn of the run that had a
decision in it, and the decision had been made at Neow:** both Bomb placers came
out of the bundle I picked. Screen and outcome agreed to the point.

---

## Fight 2 — Corpse Slug 26/26 + Corpse Slug 27/27 (both Ravenous 4)

**Turn 1** (51 HP). Mine Toss (Mine 4 on both) + Dodoco Cover on slug 2 (Bomb 4,
5 Block) + Defend. 10 Block against an 8, took 0.
*Alternative rejected:* Big Badda Boom or Rapid Fire now. Big Badda Boom reads
"Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt" — with
no Bombs down that last clause is zero, so it is a 2-energy 12. Holding it while
Bombs grew was worth more than a third of a turn's damage.

**Turn 2** (51 HP, Frail 2). Slug 1 came back at 22/26 wearing a Pyro Aura: its
Mine had gone off before its hit for 4, and Pounding Surprise paid me a Spark for
it. Played Fish-Flavored Bait on slug 1 (4 + Bomb 4), Strike slug 1, Defend
(printed **3 Block**, Frail-adjusted), Run Away! (2).
*Alternative rejected:* pointing everything at slug 2. Slug 2 was already carrying
"Bomb 16 … Bombs here: 8 / 8, including 1 Mine" — the Bombs were covering it, so
the hand's direct damage went to the bare body. Division of labour, and it was a
choice.

**Turn 3** (50 HP). Slug 1 at 12 with Bomb 8. Ka-pow!: 8 + 4 = 12, exactly lethal.
Slug 2 ate it — **Stunned, Strength 4** — so I got a free turn. Spent it on
Strike ×2 into the stunned body (19 → 7) and Jumpy Dumpty (Bomb 8, total 20).
*Alternative rejected:* Ka-pow! on slug 2 instead (12 + 4 = 16, leaving it at 3)
— that leaves slug 1 alive and swinging and gives up the Stun.

**Turn 4** (50 HP). Slug at 7 with "Bomb 28 … Bombs here: 16 / 12". Ka-pow!. Kill.
*Alternative rejected:* nothing — this is a plan set up two turns earlier paying
off, not a dead turn.

---

## Fight 3 — Toadpole 25/25 + Toadpole 21/21

**Turn 1** (42 HP). Fish-Flavored Bait on T1 (4 + Bomb 4), Strike on T2, Defend,
Run Away!.
*Alternative rejected:* Rapid Fire. It "Set[s] off a random enemy and deal[s] 3
damage to it, 4 times" — random means it cannot be aimed at the body I am
building a Bomb on, which is the whole point of the deck.

**Turn 2** (42 HP). T1 at 21 with Bomb 8 and a fresh **Thorns 2**. Jumpy Dumpty
(Bomb 8 → 16), then Ka-pow!: 16 + 4 = 20, leaving T1 on **1 HP**, and Jumpy
Dumpty's rider fired — Mine 3 on both. Then Strike on T2 and a Defend.
*Alternative rejected:* Striking T1 to finish it. Two reasons, both printed:
Thorns pays 2 back per attack, and the Mine 3 now on T1 "goes off before its
enemy's hit, which lands in full **unless the Mine kills**" — 3 into 1 HP kills.
I chose to let its own Mine do it.

**Turn 3** (40 HP). T1 had indeed died to its own Mine and its 3×3 never landed.
Last Toadpole: 9 HP, Mine 7, Thorns 2. Played **Mine Toss alone** (Mine 7 → 11)
and ended the turn. The Mine went off before its hit and killed it.
*Alternative rejected:* Strike ×2 for 12 — also lethal, also two actions, but it
pays 4 damage back through Thorns. **One card, one energy, no damage taken, no
Thorns**, because Bombs are "Not an Attack" and "no when-hit power fires". Best
decision of the act, and it came entirely off text the screen had printed.

---

## Fight 4 (Elite) — Skulking Colony 75/75, Hardened Shell 20, 14 damage

> **Hardened Shell 20 of 20 left this turn (buff)** — Skulking Colony cannot lose
> more than 20 HP each turn.

This enemy is aimed squarely at the kit, and the kit's own keyword text already
knows it: the Bomb reminder reads "only Vulnerable **and a cap** move it."

**Turn 1** (40 HP). Fish-Flavored Bait (4 damage, Bomb 4) + Defend + Defend.
*Alternative rejected:* Strike + Bait + Defend for 10 damage. Under a 20/turn cap
a spike is wasted, and a Bomb grows 4 a turn for free — so the correct shape is
block now and let the Bomb accumulate into the cap later. Took 4. **The cap turned
a normally-automatic "hit it" turn into a real decision.**

**Turn 2** (36 HP). Albedo — Solar Isotoma + Strike + Strike. 12 on the turn,
Albedo's 8 at end of turn: **exactly 20**, the cap, 71 → 51.
*Alternative rejected:* Rapid Fire or Jumpy Dumpty lines that overshoot 20 and
throw the excess away. Albedo's 4 Block was all I had; took 10.

**Turn 3** (26 HP). Big Badda Boom into Bomb 12 would have been 12 + 12 + 12 = 36;
the cap ate 16 of it. Played it anyway plus Dodoco Cover (Bomb 4, 5 Block).
Albedo added 4 Block and its 8 damage was eaten by the spent cap. Took 0. 51 → 31.
*Alternative rejected:* holding Big Badda Boom for a better turn. Under a cap
there is no better turn — 20 is 20 — so its worst moment costs nothing. That
reasoning is the finding: **the elite makes my best card indistinguishable from
two Strikes.**

**Turn 4** (26 HP). Fwoosh! (1 Spark, **0 energy**) set off Bomb 8 for 8 and hit
for 6; Fish-Flavored Bait for 4 (18 of 20); Jumpy Dumpty (Bomb 8); Run Away! for
7 Block. Colony 31 → 11, carrying Bomb 20.
*Alternative rejected:* playing the Retained Ka-pow! for its last 2 points of cap.
Deliberately kept it in hand as a **guaranteed detonator for next turn**, because
Retain is the only thing in the deck that guarantees a Set off is available when
the pile is big. Took 7 → 19 HP.

**Turn 5** (19 HP). Ka-pow!, Bomb 20 into 11 HP. Kill.
*Alternative rejected:* none. The plan paid off exactly as drawn up on turn 4.

---

## Fight 5 — Corpse Slug 26/26 + 27/27 + 25/25 (all Ravenous 4)

**Turn 1** (19 HP, 26 incoming). Used **Ghost in a Jar** (Intangible 1), then
Big Badda Boom (12, no Bombs down) + Strike (9, Strike Dummy) + Fwoosh! (6) = 27
into slug 1. Kill.
*Alternative rejected:* Defend + a partial attack, which leaves me at ~10 HP and
three live slugs.
**Where I looked stupid:** both survivors ate the corpse — both Stunned, both
Strength 4 — so nothing attacked me that turn and **the Intangible potion was
entirely wasted**. Ravenous prints "becoming Stunned"; I read it and did not read
it forward. My error, not the screen's.

**Turn 2.** Ka-pow! (4 damage, applies the Pyro Aura Albedo needs) + Albedo —
Solar Isotoma + Mine Toss. Albedo fired for 8 and 4 Block.
*Alternative rejected:* also playing the spare Defend with my third energy. I
skipped it **to save an action against the 120 cap**. The Stun had expired, slug 2
hit for 14 into 4 Block, and I went 19 → **9**. That is a budget decision costing
5 HP, not a game decision, and it nearly ended the run.

**Turn 3** (9 HP, 26 incoming, Frail). Strike (9) + Fish-Flavored Bait (4) into
slug 1 to put it on **2 HP under its own Mine 8**; Dodoco Cover on slug 2 (Bomb 4,
3 Block); Dig In (0 energy, 1 Spark, 6 Block). Total 13 Block including Albedo's 4.
*Alternative rejected:* all-in block (8 Block, no damage) — that leaves me on 1 HP
next turn; or all-in damage — that kills me if slug 2 swings first. The line was
chosen so that **either turn order survives**: if slug 1's Mine kills it first the
other is Stunned; if the other swings first, 13 Block covers 12. Took 0.
Outcome: slug 1 died to its Mine, the survivor ate it (**Strength 8**) and
**inherited every Bomb** — "Bomb 28 … Bombs here: 8 / 12 / 8" on one 21 HP body,
exactly as the keyword's "A kill moves them to a survivor" says.

**Turn 4** (9 HP). **Bomb 28 sitting on a 21 HP enemy and not one Set off card in
hand** — Run Away!, Strike ×2, Defend, Dodoco Cover. Used Cunning Potion for three
Shiv+ and killed it with Strike + Strike + Shiv+ = 24.
*Alternative rejected:* Strike ×2 to put it on 3 and let its own Mine finish it —
correct on the printed rule, but it stakes a 9 HP run on which of the three Bombs
is the Mine, and I could not tell from the panel. **The 28-damage Bomb never went
off. That is the kit's failure mode in one screen: the pile is enormous, and the
trigger is a different card that may simply not be there.**

---

## Offers

**Companion cards offered (all five):**

| Where | Card | Took? |
|---|---|---|
| Fight 1 reward | **Barbara — Melody Loop** — 1, gain 4 Block, for 3 turns apply Hydro at start of turn, Exhaust | No |
| Fight 2 reward | **Albedo — Solar Isotoma** — 1, power, Hexerei; end of turn, if any enemy has an aura, 8 damage and 4 Block | **Yes** |
| Fight 3 reward | **Charlotte — Framing: Freezing Point Composition** [Cryo] — 1, deal 4, draw 1 | No |
| Elite reward | **Amber — Fiery Rain** [Pyro] — 1, deal 4 to ALL enemies 3 times | No |
| Fight 5 reward | **Gorou — Juuga: Forward Unto Victory** [Geo] — 1, for 3 turns deal 6 Geo to a random enemy at end of turn, Exhaust | No |

**Reaction-related cards I passed for want of a second element.** This needs stating
carefully, because the honest version is more awkward than the question assumes:
**Barbara (Hydro), Charlotte (Cryo) and Gorou (Geo) were each themselves the only
second element I was ever offered.** I passed all three — Barbara for Big Badda
Boom, Charlotte for Fwoosh!, Gorou for Quick Fuse — because in each case the Pyro
or Bomb card was plainly stronger for the deck in front of me, and because one
off-element card in a 19-card deck is not a plan, it is a coin flip. The
consequence: **I played the entire act without ever seeing an Elemental Reaction**,
and every screen for eleven floors carried the same fifteen-line Elemental Reaction
block ending "NO REACTION IS REACHABLE HERE."

**Card rewards — took / nearly took:**

- Neow bundle: took Dodoco Cover / Run Away! / Rapid Fire; nearly took Sorry,
  Jean… / Pocket Match / Bang Bang! (passed: Spark-priced, and I had 1 Spark).
- Fight 1: took **Big Badda Boom**; nearly took Barbara — Melody Loop.
- Gorge event (2 of 8 commons): took **Mine Toss** and **Fish-Flavored Bait**;
  nearly took Coven Errand (Bomb 5) and Ammo Scavenging (Bomb 4 + draw).
- Fight 2: took **Albedo — Solar Isotoma**; nearly took Powder Charge (Bomb 6 for
  1 Spark — my Sparks were idling at 4).
- Fight 3: took **Fwoosh!**; nearly took Charlotte.
- Elite: took **Dig In** (8 Block for a Spark, at 19 HP); nearly took Amber —
  Fiery Rain.
- Fight 5: took **Quick Fuse**; nearly took Gorou. Quick Fuse because turn 4 of
  that same fight had just shown me the hole — a detonator that costs no energy.

**Events:** Room Full of Cheese → Gorge (2 of 8 commons) over Search (−14 HP for a
+1 Max HP relic). The Legends Were True → Slowly Find an Exit (−8 HP, 1 potion)
over the Spoils Map, because the Map is an Unplayable card clogging an already
17-card deck and pays out in an act I was never going to reach.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

- **At the draft, Neow:** energy-priced bundle vs Spark-priced bundle. The trade
  was "cards I can cast on turn 1" against "cards that are better once the engine
  is running". It decided the shape of every fight afterwards, and it is a genuinely
  hard read from the two screens alone.
- **On the turn, fight 3 turn 3:** Mine Toss vs Strike ×2. Identical kill, and the
  Bomb route costs no HP because Bombs are not Attacks and Thorns never fires.
  This is the kit at its best — the printed rules produced a line I would not have
  found in the base game.
- **On the turn, elite turns 1 and 4:** the 20/turn cap inverted the normal
  instinct. Turn 1 the right play was to block and let the Bomb grow for free;
  turn 4 the right play was to *not* play a free 0-cost attack, because Retain
  made it a guaranteed detonator for a pile I could not otherwise be sure of
  popping. Both were decided by reading a rider, not by counting damage.
- **Earlier in the fight, fight 5 turn 3:** routing exactly enough damage to put a
  slug under its own Mine, so its attack never lands, while keeping enough Block
  that either turn order survives. Two printed rules combined into one line.
- **At the draft again, floors 8 and 11:** picking Fwoosh! and Dig In as **Spark
  sinks**. I finished fight 2 sitting on 4 unspent Sparks with nothing to spend
  them on. That is the deck-building decision the relic actually poses, and it took
  me eight floors to notice it.

**(b) What felt automatic, and what never seemed worth playing.**

- **Every turn where the hand was Strikes and Defends.** Fight 1 turn 1 is the pure
  case: 3 energy, four identical Strikes, one 0-cost Block. There is nothing to
  decide.
- **Rapid Fire never once earned 2 energy.** "Set off a random enemy" means it
  cannot be pointed at the body I have spent two cards bombing, which is the only
  thing the deck is trying to do. In every hand it appeared in, a Strike or a Bomb
  placer was better. It is the card I most wanted to remove.
- **Big Badda Boom against the capped elite** printed 36 and delivered 20, and no
  sequencing changed that. Against a cap it is a Strike that costs 2.
- **Run Away!'s conditional almost never turned on.** "+4 additional Block if a Bomb
  went off this turn" wants a detonation on *my* turn, but Mines go off on the
  *enemy's* turn and my detonators are the turns I am spending on damage. I think I
  collected the bonus once in five fights.
- **Defend after Frail** is 3 Block for 1 energy and feels like a non-card.

**(c) What I could not understand, or that contradicted its own printed text.**

- **Nothing contradicted its printed text.** Every number I predicted off a screen
  landed: 4 + 8 printed as "Bomb 12" and dealt 12; Mine 11 killed a 9 HP body before
  its hit; the elite took exactly 20 on three separate turns; the inherited-bombs
  rule moved 28 points onto a survivor exactly as written. Card text is also
  **live-adjusted for my debuffs** — Rapid Fire printed "2 damage" under Weak,
  Defend printed "3 Block" under Frail — which is the single best legibility
  feature in the build and made turn planning trustworthy.
- **Ravenous, I could not read.** "When an enemy dies, Corpse Slug immediately eats
  it, becoming Stunned and gaining 4 Strength" is singular, and both survivors ate
  the same corpse and both got Stun and Strength. I wasted an Intangible potion on
  that misreading. The screen does not say whether one or all eat.
- **The Elemental Reaction block is the largest piece of text in the game and I
  never used it once.** Fifteen lines, on every screen, for eleven floors, most of
  it about a hidden interaction ("THAT LAST RULE CAN HIDE THE FIRST…") that cannot
  arise while Pyro is the only element on offer. The page itself keeps saying
  "NO REACTION IS REACHABLE HERE". A blind reader spends a lot of attention on it
  before concluding it is inert, and the only cards that would switch it on were
  the four Companions I kept correctly declining.
- **The Spark economy has a visible chicken-and-egg at Neow.** Sparks come from
  Bombs going off; Bombs need a placer; the Spark-priced bundle's placer *is*
  Spark-priced (Bang Bang!, 2 Sparks, against a starting 1). I could read that off
  the screen, but only because the tooltips spelled out both halves.
- **Minor:** the map's deck list showed `Shiv+ ×3` (potion tokens) and omitted
  Albedo — Solar Isotoma, which was in play as a power. It prints a caveat saying
  it is the last fight's snapshot, so it is not lying, but it is not the deck.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Rapid Fire** — random targeting is anti-synergy with a deck whose
whole plan is to load one body. Happiest to draw: **Ka-pow!** — 0 cost, Retain,
and it converts whatever the Bomb pile has grown into on *my* schedule. It killed
three enemies outright and, on elite turn 4, the correct play was to hold it
unplayed, which is more than most 0-cost cards can offer. Fwoosh! is the same job
for a Spark I was not otherwise spending, and was the pick that fixed the run.

**(e) Did the first turn of the first fight already present a decision?**

**No.** Fight 1 turn 1 was Strike ×4 and Run Away! against one 38 HP enemy with 3
energy — the only question was which three of four identical Strikes to play. The
kit's first real decision arrived on **fight 1 turn 3**, when Dodoco Cover, Jumpy
Dumpty and Ka-pow! were in hand together, and even that was reachable only because
**both Bomb placers came from the Neow bundle**. On the starting deck alone, the
first Bomb card I saw was Ka-pow!, a detonator with nothing to detonate.

---

## Non-blindness declaration

Commands run outside the two allowed forms:

- `mkdir -p` twice — once for an unused scratch directory under the session
  scratchpad, once for `review/qa/klee-round-17-2026-09-05/` to hold this file.
- `cd` into the working directory as the prefix of Bash calls.
- `sed -n '<ranges>p'`, `head -60`, and `>/dev/null` used purely to trim or suppress
  the output of `observe` and `act` so the same screens did not fill my context.
  These reformat output I was already entitled to see; they showed me nothing new.
- `echo ok` twice, to confirm the mkdirs.

Tools used: **Bash** (for the two allowed blindplay commands and the scratch
commands above) and **Write** (once, for this file).

I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy command. I never used `GITS_LANE=1`.

**Repo files read: none.**
