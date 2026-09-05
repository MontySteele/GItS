# Blind seat — KLEEMOD-KOKOMI, lane 1, round 19 (targeted)

## Identity

- **Model / seat:** Opus, blind TESTER seat, lane 1.
- **Run seed:** `Y2W6AK7KW2F1`. **Ascension:** 2. **Character:** the Bake-Kurage
  kit (Kokomi arm) — the run opened at HP 64/80.
- **Act:** 1. The map named the act boss as **Waterfall Giant** (16 floors).
  I never reached it.
- **Actions accepted:** 120 of 120.
- **Termination:** action budget. The bridge printed `actions: 120 of 120` on
  the `end turn` that closed my round-3 turn of the floor-12 **Elite (Terror
  Eel)**. I stopped there, mid-fight, alive. Wall clock was nowhere near the cap
  and I hit no refusals and no stalls.
- **HP trajectory:** 64 → 58 → 51 (f2 Corpse Slugs) → 45 → 37 (f3 Seapunk) →
  30 → 28 (f4 Toadpoles) → 18 (f5 Cultists) → 16 (f8 Gremlin Merc) → 11 (f11
  Punch Construct) → **2/80** (f12 Terror Eel, still standing).
- **Gold at stop:** 52 (99 start, +12/+13/+19/+15/+12 from fights, −55 event
  enchant, −24 Salt Line, −75 Card Removal; the Gremlin Merc's `Thievery 20`
  took 20 when it hit me and the Fat Gremlin escaped with it).
- **Potions held:** Attack Potion (1 of 3 slots). Spent: Explosive Ampoule (f5),
  Fire Potion (f8).
- **Relics:** Tamakushi Casket (start), Neow's Talisman, Miniature Cannon
  (random relic from *This or That?*), Parrying Shield (floor-10 chest).
- **Deck at stop (18 cards):** Defend ×3, Defend+, Exposed Flank, Feigned
  Retreat, Flank, Kirara — Surprise Dispatch, Kurage's Oath, Nereid's Ascension
  (Steady), Pincer, Ripple, Salt Line ×2, Sango Isshin, Shikanoin Heizou —
  Heartstopper Strike, Slack Water+, Strike ×4. (Clumsy was bought out at the
  shop.)

**Neow pick: Neow's Talisman** — "Upgrade 1 of your Strikes and 1 of your
Defends." I knew nothing about the kit, so I took the pick that changes the
least and lets me read the base cards as printed; Dowsing Rod wants five ?
rooms I might never see, and Winged Boots buys route freedom I could not yet
value.

**A note on that pick, because it did not do what it said.** After it resolved,
the deck census showed `Defend+` and `Slack Water+` — and four unmodified
Strikes, in every hand, all run. I never once saw a `Strike+`. Either the
Talisman's Strike half landed on Slack Water (a kit attack) instead of a Strike,
or its Strike half did nothing. I cannot tell which from the screen; I can only
say the relic printed "Upgrade 1 of your Strikes" and no Strike in my deck was
ever upgraded. This also cost me Miniature Cannon value later (+3 to *upgraded*
Attacks), which only ever applied to Slack Water+.

---

## Fight 1 — floor 1: Corpse Slug (1) [A] 27 HP, Corpse Slug (2) [B] 25 HP

Both carried `Ravenous 4` — "When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength."

| Turn | Plans written that turn | Carry-outs at the start of the next turn |
|---|---|---|
| 1 | Slack Water+ | Slack Water+ ×2 (Nereid doubling) |
| 2 | Kurage's Oath, Flank | Kurage's Oath ×2, Flank ×2 — fight ended here |

**Turn 1.** Played **Nereid's Ascension** (2) then wrote **Slack Water+** on the
Bake-Kurage (1). *Rejected:* the tempo line — Slack Water+ on B for 7+Weak plus
both Strikes, 21 damage into a 25 HP body — because I wanted to know what the
doubling power actually did before the fight was decided, and turn 1 against a
Debuff intent and a 3×2 attack was the cheapest turn to find out. Cost: I dealt
zero and took 6.

**Turn 2.** Wrote **Kurage's Oath** and **Flank** as Plans, played **Defend**.
*Rejected:* playing all three now for 15 face damage, which kills neither slug.
The screen gave me the arithmetic to reject it: with `Nereid's Ascension`
up, "The jellyfish carries out EVERY Plan twice", so 7-to-ALL and
8-to-each-attacker become 14 and 16 apiece — 30 on each body against 23 and 21.
I also weighed *Flank vs Feigned Retreat* and took Flank knowing its Plan is
conditional ("each enemy that **intends to attack**") and that I was betting on
next turn's intents, not this turn's; that was the only genuine risk in the
turn.

**Outcome.** Both slugs died inside the carry-out, and the rewards screen printed
the whole beat rather than swallowing it — a good touch. The carry-out log also
showed the second Flank hitting only the survivor for 1, so the doubling does
not waste itself on corpses.

**One printed defect.** The carry-out line read, verbatim:

> `Bake-Kurage: Flank: LocString table monsters entry CORPSE_SLUG.name, LocString table monsters entry CORPSE_SLUG.name, 8 — the 8 is damage.`

An unlocalised LocString key leaked into the player-facing log where the enemy
names belong. It recurred on floor 5 with `CALCIFIED_CULTIST.name` /
`DAMP_CULTIST.name`. Only Flank's "each enemy that intends to attack" line does
this — Kurage's Oath, Pincer and Feigned Retreat all printed clean.

**Companion cards:** offered *Lynette — Enigmatic Feint* (Swirl an aura onto
ALL, gain 5 Block) — **not taken**; Swirl was worthless with Hydro as my only
element and no second element in sight. Took **Exposed Flank** instead.
**Companion cards played this fight: 0.**

---

## Fight 2 — floor 3: Seapunk [A] 46 HP

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | Kurage's Oath, Pincer | Kurage's Oath (7), Pincer (9) — no Nereid, single carry-outs |
| 2 | none | — |
| 3 | none | fight ended |

**Turn 1.** Wrote **Kurage's Oath** and **Pincer** as Plans, played **Defend**.
Nereid was not in hand. *Rejected:* the same cards played on the face for 3+6=9
now, against 7+9=16 arriving next turn — a real trade of one turn of 11 incoming
damage for +7 damage. I took the delay because 46 HP is a three-turn body either
way.

**Turn 2 — the best decision of the run, and it was against the kit's own
grain.** Hand: Nereid's Ascension (now Steady/Retain), Defend, Strike ×2,
Exposed Flank. I played **Exposed Flank on the face** (1 Vulnerable), then both
**Strikes**. *Rejected:* writing Exposed Flank as a Plan, which the kit's whole
shape pushes you toward. Playing it now made the two Strikes 9 each instead of
6, and the relic's own ping rode the Vulnerable too — Seapunk went 30 → 9, i.e.
21 damage, so the Casket's "2 Hydro" landed as 3. Twenty-one damage now beat
"2 Vulnerable next turn plus 12". **The decision was live because the same card
has two different bodies depending on where you point it**, and here the wrong
one was the flashy one.

**Turn 3.** Seapunk at 9 with a Buff+Defend intent. Played **Slack Water+**
alone: 7 damage plus the Casket's 2 off the Weak = exactly 9. *Rejected:* Flank
+ Strike for a guaranteed 14, because killing before it blocked was worth the
exact-lethal risk and I wanted to see whether the debuff ping resolves before
or after the card's damage. It resolves inside the same beat and the kill went
through.

**Companion cards:** offered *Chevreuse — Vanguard's Valor* (0 cost, next Attack
+3, +3 more if an Elemental Reaction triggered this turn) — **not taken**; the
second clause was dead text on a screen that had just told me "NO REACTION IS
REACHABLE HERE". Took **Ripple**. **Companion cards played: 0.**

---

## Fight 3 — floor 4: Toadpole (1) [A] 21 HP, Toadpole (2) [B] 25 HP

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | Pincer | Pincer ×2 (9 + 9) |
| 2 | Kurage's Oath, Feigned Retreat | Kurage's Oath ×2 (7+7), Feigned Retreat ×2 (6+5) — fight ended |

**Turn 1.** Hand was three Defends, Pincer and Nereid — the flattest hand of the
run. Played **Nereid's Ascension** (2) and wrote **Pincer** (1). *Rejected:*
Nereid + Defend+ (8 block, eat nothing, write nothing), because against two
buffing bodies a turn spent blocking a 7 is a turn the enemies spend growing.
The rejected alternative here was thin — with three Defends in hand the turn was
close to automatic once I decided Nereid was going down.

**Turn 2 — the fight's real decision.** A was at 3 HP with `Thorns 2` and a 3×3
intent; B was untouched at 25 with a Buff intent. I killed A with a plain
**Strike**, then wrote **Kurage's Oath** and **Feigned Retreat**. *Rejected:*
killing A with Kurage's Oath instead, which also splashes 3 onto B — I rejected
it because Kurage's Oath is worth 14-to-ALL as a doubled Plan and 3 on the face,
so spending it as a finisher on a 3 HP body burns the best card in the deck to
save a Strike. The arithmetic was exact and the screen let me do it in advance:
14 (Oath ×2) + 12 (Feigned Retreat ×2) = 26 against B's 25. It killed on the
nose.

**Note on the Thorns test:** I never learned whether the Bake-Kurage's planned
hits take Thorns damage on my behalf, because A died to a hand card before any
Plan hit it. That is an open question, not a finding.

**Companion cards:** offered *Shikanoin Heizou — Heartstopper Strike* (Anemo,
6 damage, +4 per Swirl) — **taken**, mostly because it was the only second
element I had been shown and the screens kept promising six reactions I could
not reach. **Companion cards played: 0.**

---

## Fight 4 — floor 5: Calcified Cultist [A] 41 HP, Damp Cultist [B] 52 HP

Both opened on Buff intents and both had Ritual (A: +2 Strength a turn; B: **+5**
a turn). This is the fight that took me from 28 to 18 and shaped the rest of the
act.

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | Exposed Flank, Kurage's Oath (in that order) | Exposed Flank (2 Vuln + Casket 3 each), Kurage's Oath (10 each — "the clause asked for 7") |
| 2 | Flank | Flank ×2 (12 each, twice) — killed A, left B at 5 |
| 3 | none | fight ended |

**Turn 1.** Wrote **Exposed Flank** first, then **Kurage's Oath**, then played a
**Strike** on A. *Rejected:* playing Nereid on the free turn (both enemies were
buffing, so nothing hit me) and writing only one Plan. I rejected it because
**Plan order is a real lever**: the carry-out log resolves Plans "front first"
in the order written, so putting Vulnerable ahead of the damage Plan multiplies
it in the same beat. It did: the log printed

> `Bake-Kurage: Kurage's Oath, 10 — the 10 is damage; the clause asked for 7.`

That "the clause asked for 7" clause is the single best piece of writing on any
screen in this run. It told me my ordering had worked without my having to do
arithmetic against a hidden number.

**Turn 2.** Used **Explosive Ampoule** (10 to ALL), played **Nereid's Ascension**
(2), wrote **Flank** (1). *Rejected:* the pure tempo line — Flank + 2 Strikes on
A at Vulnerable rates, which came to 12+9 = 21 against A's 22 and left it alive
by one. What made this decision live was that **Flank's printed face had already
updated to the Vulnerable-adjusted number**: it read "Plan: Deal **12** damage to
each enemy that intends to attack", not 8. I could see 12 × 2 carry-outs × 2
bodies = 48 before committing, against two enemies both showing attack intents.
It paid: A died, B fell 39 → 15, and the potion had put it in reach.

**Turn 3.** B at 5 HP with a Hydro aura on it. Played **Shikanoin Heizou —
Heartstopper Strike** to kill it, specifically to see the Anemo/Hydro reaction
fire. It killed; the fight ended before any screen could show me what the Swirl
did. **Companion cards played this fight: 1 (Heizou).**

**Companion cards:** offered *Kirara — Surprise Dispatch* (8 Block, and 10
damage next turn, for 1) — **taken**. At 18/80 it was the best rate on the
screen and it is the card that later kept me alive on floors 8 and 12.

---

## Fight 5 — floor 8 (an Unknown room that opened into combat): Gremlin Merc [A] 47 HP

47 HP, `Thievery 20`, `Surprise 1` ("Something is off about this creature..."),
opening on 7×2 = 14 into my 18 HP.

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | none | — |
| 2 | Ripple | Ripple (1 Energy + 4 Block) |
| 3 | none | fight ended |

**Turn 1.** Played **Kirara** (8 block) and **Feigned Retreat** (4 block) for 12
against 14, then **Fire Potion** (20) and **Pincer** (6). *Rejected:* writing
anything as a Plan. At 18 HP against a 14-damage opener, a Plan is a promise
that pays next turn and I might not have had one; every point of this turn's
energy had to be block or face damage. **This is the shape of the kit's failure
mode: the Plan engine is a tempo loan, and when you are under the incoming
damage curve you cannot afford to take out the loan.**

I also used the Fire Potion *before* Pincer deliberately, hoping Pyro would
leave an aura that Pincer's Hydro would Vaporize. **It left no aura at all** —
the enemy block showed no Pyro after 20 damage. So the potion is elementally
inert. That is a legitimate design choice, but the screens spend a very large
paragraph on reactions and nothing tells you which sources apply an element.

**Turn 2.** Merc at 11 after Kirara's delayed 10 landed. Killed it with **Flank**
+ **Strike**. *Rejected:* Heizou for the Swirl (the Merc had a Hydro aura) —
rejected because I only had 3 energy and needed certain lethal, not a reaction
demo.

**Then `Surprise 1` fired: the Merc split into Sneaky Gremlin [A] 13 and Fat
Gremlin [B] 15, both Stunned.** With 1 energy left I wrote **Ripple** as a Plan
(0 cost) and played a **Strike**. *Rejected:* Ripple on the face for 2 Block —
against two Stunned bodies block is worth nothing and the Plan line pays "1
Energy and 4 Block", so this was the one moment where the Plan was strictly
free.

**A contradiction between two screens.** Every battle screen prints:

> *Each enemy keeps its letter and its number for the whole fight: a body that
> dies does not renumber or re-letter the ones still standing, and a summon
> takes the next free letter.*

The Gremlin Merc was **[A]**. It died. Sneaky Gremlin came in as **[A]** and Fat
Gremlin as **[B]**. The letter moved. I had been aiming by letter all fight and
this is exactly the case the paragraph promises will not happen.

**Turn 3.** Ripple's carry-out printed `Ripple, 1 — the 1 is Energy` and gave me
Energy 4/3 and 4 Block. Played **Exposed Flank** on Sneaky (Casket 2 + Vuln),
then **Kurage's Oath** on the face — 3 × 1.5 rounded up to 5 and killed it,
which was one point better than I had predicted. Fat Gremlin escaped with my
gold; I had no attack left in hand to stop it and chose not to burn the Attack
Potion on 12 HP I could not finish.

**Companion cards:** offered *Kamisato Ayato — Kyouka* on the next screen (see
fight 6). **Companion cards played this fight: 1 (Kirara).**

---

## Fight 6 — floor 11: Punch Construct [A] 55 HP

`Artifact 1`, opening on a Defend intent.

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | none | — |
| 2 | Kurage's Oath, Pincer | Kurage's Oath (7), Pincer (9) |
| 3 | none | fight ended |

**Turn 1.** Played **Slack Water+** (10 — Miniature Cannon's +3 was visible on
the face), **Flank** (8) and a **Strike** (6). *Rejected:* writing Plans,
because the Construct was *defending this turn*: block it gains on its own turn
sits there through my next turn, so damage aimed at my next turn lands into 10
block and damage aimed now lands on raw HP. Leading with Slack Water+ was also
deliberate — its Weak is eaten by `Artifact 1`, which strips the Artifact for
free and clears the way for later debuffs. **That is the one place all run where
a card's *worst* clause was the reason to play it.**

**Turn 2.** Construct at 31 with 10 Block, intending 5×2 plus a debuff, me at 16
with no block. Played **Defend** (5) and wrote **Kurage's Oath** and **Pincer**.
*Rejected:* Heizou for a Swirl-boosted 10, which would have eaten exactly the 10
block and dealt nothing to HP — a nicely-shaped trap the screen let me see
through, since enemy Block is printed on the body line. The Plans arrived at my
turn 3, after its block had cleared, for 16 to the face.

**Turn 3 — the pay-off, and the card I would call the kit's best.** Construct at
15, intending **14** into my 11 HP. I played **Sango Isshin**:

> "Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter
> of your Max HP to ALL enemies instead."

Two Plans had carried out that turn, so it read 20 to ALL and killed. *Rejected:*
Salt Line + Defend+ + Kirara for ~19 block and a fourth turn — rejected because
Sango Isshin turned a lethal turn into a won fight. **This is the plan engine
paying off exactly as designed: the condition was set two turns earlier by a
decision that was about enemy block, not about Sango Isshin at all.** I did not
have Sango Isshin in hand when I wrote those Plans. It still counts as the plan
paying off, because the deck was built so that *any* Plan turn arms it.

**Companion cards:** offered *Sayu — Naptime* — **not taken**; I took the second
Salt Line at 11 HP. **Companion cards played: 0.**

---

## Fight 7 (unfinished) — floor 12 Elite: Terror Eel [A] 140 HP

`Shriek 70` — "The first time Terror Eel's HP reaches 70 or below, it becomes
Stunned." I entered at 11/80 because the map offered exactly one node and it was
this one.

| Turn | Plans written | Carry-outs next turn |
|---|---|---|
| 1 | Ripple | Ripple (1 Energy + 4 Block) |
| 2 | none | — |
| 3 | none | **budget reached** |

**Turn 1.** Incoming 16 into 11 HP. Wrote **Ripple** (0) and played **Kirara**
(8), **Defend** (5), **Feigned Retreat** (4) — 17 block. *Rejected:* Ripple on
the face for 2 more block; 17 already cleared 16, so the Plan line was free
value. Took zero damage. Parrying Shield fired off the ≥10 block and Kirara's
delayed 10 landed, so a turn I spent entirely on defence still moved the eel 16.

**Turn 2.** 4 energy (Ripple's carry-out). Played **Slack Water+** (10 + Weak,
Casket 2), **Pincer** (6), **Defend+** and **Defend** (17 block against 9).
*Rejected:* writing Plans — with `Nereid's Ascension` still undrawn a Plan is
worth only its single carry-out, and the eel's 3×3-plus-Buff turn was survivable
by block. Honest assessment: **without Nereid in hand, writing a Plan is usually
a small loss, and I had drawn it in only 4 of 7 fights.**

**Turn 3.** Eel at 100, `Vigor 6`, intending **22** into my 11. Max block in
hand was Salt Line (8) + Defend (5) = 13, so 9 was going through no matter what.
Played both plus a **Strike**, ended the turn at **2 HP** — and that `end turn`
was action 120. Round over on the budget, mid-fight, alive, with Nereid's
Ascension retained in hand and Sango Isshin drawn one turn too late.

**Companion cards played: 1 (Kirara).**

---

## The kit, after 7 fights (6 finished)

### (a) Which decisions felt like real choices, and what they traded off

1. **Play-now versus write-it-on-the-jellyfish.** Every Plan card is two cards,
   and which one you hold depends on this turn's incoming damage and whether the
   enemy is about to gain block. Three examples, each decided on the turn:
   Exposed Flank *on the face* in fight 2 (Vulnerable multiplying the same
   turn's Strikes: 21 damage, versus 12 next turn); Kurage's Oath *as a Plan* in
   fight 6 turn 2 (because 10 enemy Block would have eaten it now and would be
   gone by the carry-out); Ripple *as a Plan* whenever a turn was already safe,
   because "1 Energy and 4 Block" next turn beats 2 Block now only when you can
   afford the wait. This is the kit's good axis and it is genuinely good.
2. **Plan ordering, made on the turn.** Plans carry out in the order written, so
   Exposed Flank before Kurage's Oath is 10 damage and the reverse is 7. The log
   line "the 10 is damage; the clause asked for 7" made the lever legible.
3. **What to spend the 3rd energy on when Nereid is down** — decided on the
   turn, and usually a straight trade of ~5 block against ~6 face damage.
4. **The draft decisions that shaped fights.** Taking Exposed Flank on floor 2
   is what made every later Plan turn worth 50% more; taking Sango Isshin on
   floor 8 is what won fight 6. Fight 6's turn-3 lethal looks obvious on the
   turn and was not — it was a floor-8 draft pick plus a turn-2 decision about
   enemy block.
5. **Whether to play Nereid's Ascension at all in a given fight** — a 2-energy,
   zero-immediate-effect card at 18 HP. I said yes in fights 1, 3 and 4 and no
   in fights 5, 6 and 7. That is a live call and it went both ways.

### (b) What felt automatic, and what never seemed worth playing

- **Strike.** Four of them, all unupgraded, 6 damage, no Plan line, no element,
  no interaction with the Bake-Kurage. In a deck where every other card asks
  "now or next turn?", Strike asks nothing. It was filler in every hand it
  appeared in and it is the reason my defensive turns had no damage attached.
- **Defend.** Same, minus the damage. Necessary, never interesting.
- **Turn 1 of a fight where Nereid was not in hand** was close to automatic:
  write the biggest Plan, block with what's left.
- **Pincer** never presented a decision. 3×2 now or 3×3 next turn is a 3-damage
  difference on a card too small to change any turn; I wrote it as a Plan five
  times out of habit rather than judgement. As one of the four cards handed to
  me for this round, it is the weakest of them by a distance.
- **Heizou's second clause** ("+4 for each Swirl this turn") was never live:
  one enemy meant Swirl copied an aura onto nobody, and the only time I played
  him the fight ended in the same beat.

### (c) What I could not understand, or that contradicted its own printed text

1. **The enemy-letter invariant is false.** Printed on every battle screen:
   "a body that dies does not renumber or re-letter the ones still standing, and
   a summon takes the next free letter." The Gremlin Merc was [A]; it died; the
   Sneaky Gremlin that replaced it was **[A]**. I aim cards by letter.
2. **`LocString table monsters entry CORPSE_SLUG.name`** printed raw in the
   carry-out log, twice in fight 1 and twice in fight 5. Only Flank does it.
3. **Neow's Talisman's Strike half never landed** (see Identity). Four Strikes,
   zero upgraded, all run.
4. **The map's deck census silently drops a Power you played.** On floor 2 it
   listed 13 cards and omitted Nereid's Ascension, which I had played that
   fight; on floor 11, where I never drew it, it was listed. The footnote
   ("your deck as it stood in the last fight") does not warn you that a played
   Power vanishes from the count.
5. **The reaction system is a large body of printed rules I could not use.**
   Every screen carried a ~150-word Elemental Reaction paragraph ending "NO
   REACTION IS REACHABLE HERE", all act long. When I finally bought an Anemo
   card, the one time I played it the fight ended in the same beat and I never
   saw what a Swirl does. The Fire Potion, which I used specifically to set up a
   Vaporize, **left no Pyro aura at all** — and nothing on any screen says which
   sources apply an element and which do not. Six reactions are defined at me
   repeatedly; I finished the act having observed zero.
6. **Feigned Retreat's Plan line is oddly flat**: "Gain 4 Block and deal 6
   damage" against a face of "Gain 4 Block". The Plan adds damage but not block,
   so the block half is strictly worse for waiting, which makes the card read
   confusingly — the two halves of the choice point in opposite directions.
7. **Minor:** `Surprise 1 (buff) — Something is off about this creature...` is
   flavour where a mechanic lives; it split the Merc into two bodies and I had
   no way to plan around it.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted: Strike.** Six damage, no line, no element, no Bake-Kurage
  interaction; four copies clogging a deck whose whole identity is the second
  clause. **Of the four cards added for this round, the one I never wanted was
  Pincer** — it has a Plan line, so it is not dead, but its two halves are three
  damage apart and I never once thought about it.
- **Happiest to draw: Kurage's Oath.** One energy, and its two bodies are 3-to-
  ALL now versus 7-to-ALL later (14 doubled, 21 through Vulnerable). It was the
  card I built every turn around. Runner-up, and the more exciting draw:
  **Sango Isshin**, which converts "I wrote a Plan this turn" into 20 to ALL and
  won fight 6 outright.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a sharp one.** Turn 1, floor 1, 3 energy, two Corpse Slugs, and a
hand holding both a 2-cost Power whose only text was "the Bake-Kurage carries
out every Plan twice" and a Slack Water+ that reads 7 damage on the face and
"Apply 2 Weak to ALL enemies" as a Plan. The choice — 21 face damage now versus
zero damage, 6 HP taken, and an engine that doubles everything after — is the
kit's central question, and it was on the table before I had played a card. I
took the engine line, it cost me 6 HP, and it killed both slugs one turn later.
I would call that the strongest single thing about this kit: **the opening turn
is the thesis statement.**

### One structural verdict, since the fights all pointed the same way

The Plan engine is a **tempo loan**. Every Plan trades this turn's effect for a
bigger one next turn, and `Nereid's Ascension` doubles the repayment. That is
excellent when you are ahead and unusable when you are behind — and I spent
floors 5 through 12 behind, at 28, 18, 16, 11 and 2 HP, watching hands where the
correct play was "block with three Defends and write nothing." **The kit's
decisions are richest exactly when the run is going well, and evaporate exactly
when it is not.** Every fight I lost HP in, I lost it on a turn where the Plan
board sat empty because I could not afford to fund it. Whether that is a defect
or the intended risk curve is a design call, not mine, but it is the single
clearest pattern in this act.

---

## Non-blindness declaration

- Commands run in the game: **only** `GITS_LANE=1 python -m understudy.blindplay
  observe` and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`. No
  `harness state`, no `scenario`, no `staged_turn`, no `soak`, no other
  understudy subcommand. I never used `GITS_LANE=2`.
- Other Bash usage, all of it my own scratch or plumbing:
  - `mkdir -p .../scratchpad/lane1 && echo ok` (a scratch directory I ended up
    never writing to).
  - `mkdir -p .../review/qa/kokomi-round-19-2026-09-05 && echo ok` (the record
    directory).
  - Many `observe` calls piped through `sed -n '<ranges>p'` to re-read one block
    of the screen instead of the whole page. On one such call my own overlapping
    `sed` ranges duplicated the enemy block in the output; that was my pipeline,
    not the game's print.
- Other tools: the **Write** tool, once, for this file. Nothing else.
- **Repo files read: none.**
