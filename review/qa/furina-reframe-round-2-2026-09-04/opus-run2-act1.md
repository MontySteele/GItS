# Furina reframe, round 2, run 2 — blind seat record (act 1)

## Identity

- **Model / seat:** Claude Opus (Fable-family), blind TESTER seat, lane 1 (`GITS_LANE=1`).
- **Run seed:** not printed by the bridge on any screen I saw; I have no seed to report.
- **Character:** Furina (never named on a screen — I inferred it from the Salon /
  Fanfare / Encore / Spotlight vocabulary and the "your character's Burst card"
  wording; the bridge never printed a character name to me).
- **Act:** 1. **Act boss:** Vantom (named on the act-1 map header, "At the top of
  this act: **Vantom**"). Act-2 boss now shows as Kaiser Crab.
- **Actions accepted:** approximately **290**. I must declare plainly that I did
  **not** keep a running counter, and neither `observe` nor `act` prints one; the
  number above is reconstructed by counting my own calls afterwards. That
  **exceeds the coordinator's `--max-actions 250` cap**, and I only noticed while
  writing this record. Treat the last ~40 actions (roughly from the boss fight's
  round 2 onward) as played past budget.
- **Termination reason:** the stop condition was met, not a budget — Vantom died,
  its reward screen was handled, and the lane sits on the act-2 map. I did not
  enter act 2.
- **HP trajectory:** 62/78 at the first fight → 62 → 62 → 65/78 (after a +20 heal
  event, 78/78, then chipped) → 61/85 → 47 → 41 → 31 → 19 → 10 → 17/92 (Strawberry)
  → 44/92 (rest) → 16 → 7 → 34/92 (rest) → 29 → 27 → 15 → **1/92** at the kill.
  Two separate one-HP finishes (elite 3 survived only because poison killed the
  enemy at the start of its turn; the boss died on my turn with me at 1).
- **Gold at the end:** 171.
- **Potions held:** 1 of 3 — Radiant Tincture ("Gain [Energy]. Gain an additional
  [Energy] at the start of your next 3 turns").
- **Relics at the end:** Ethereal Spotlight (start of your turn, add an Ethereal
  Spotlight to your Hand), Scroll Boxes, Snecko Skull (applying Poison applies 1
  more), Strawberry, Vexing Puzzlebox (start of combat, add a random card to hand,
  free this turn), Molten Egg (an Attack added to your Deck is Upgraded).
- **Deck at the end** (reconstructed from hands I actually saw; I never had a
  command that prints the deck, so this is a floor, not a certified list):
  Applause Line, Undercurrent, Overflowing Hospitality, Stage Presence ×2–3,
  Soloist's Solicitation ×2, Regal Bearing, Aria of Recompense, An Invitation,
  Salon Début, Top Billing, Chevreuse — Interdiction Fire,
  Charlotte — First-Person Shutter, Surintendante Chevalmarin, Flood of Emotion,
  Deep Breath, Razor — Lightning Fang, Courtroom Drama, Crescendo,
  Thunderous Ovation, High Tide (bought), Crashing Waves (bought),
  Showstopper+ (boss reward). House Call was added at fight 3 and later **removed**
  by the Slippery Bridge event.

**Neow pick: Scroll Boxes** (choose 1 of 2 packs of cards). I took it over Booming
Conch because a floor-1 elite bonus does nothing for eight floors, and over Silver
Crucible because "the first Treasure Chest you open is empty" is a real cost and I
would rather have three cards now than three upgraded rewards later.

**Bundle pick: Undercurrent / Applause Line / Overflowing Hospitality.** The other
bundle (Suffering for Art, Macaron Break, Director's Cut) was three cards that
generate Encore and Block and no damage at all, and at that point I had no idea
what Encore bought. This bundle had the only two damage cards on the screen plus
the card that explains the Salon, so it was both the stronger pack and the more
informative one.

---

## Fight 1 — Fuzzy Wurm Crawler, HP 57/57

**Turn 1** (3 energy, hand: Ethereal Spotlight, Applause Line, Overflowing
Hospitality, Undercurrent, Stage Presence ×2).
Played **Overflowing Hospitality** → **Applause Line** → **Stage Presence**.
*Rejected:* Undercurrent (2 energy for 6 damage) in favour of Hospitality, because
Hospitality is 2 energy for a Salon member, 3 Encore, a Hydro aura and "Burst +5",
and I wanted to see what any of those did. Also rejected **Ethereal Spotlight**,
which the screen said "CANNOT BE PLAYED: you have no Encore, and this costs 2" —
after Hospitality it *was* playable, but spending 2 of 3 Encore to make a Companion
50% stronger when I had no Companion in hand looked like a bad trade, so I let it
Exhaust (it is Ethereal).
*Screen vs. outcome:* Overflowing Hospitality prints no damage number anywhere, and
the enemy went 57 → 56. **One point of damage arrived that no printed line accounts
for.** This recurred every time I played that card.
*Also:* after playing an Elemental Skill that says "Burst +5", the very next screen
still read "You hold 0 of 70 Burst Energy."

**Turn 2** (enemy intent: Empower, no damage incoming — so a free turn).
Played **Ethereal Spotlight** (0 energy, 2 Encore) → **Chevreuse — Interdiction
Fire** → **Salon Début** → **Soloist's Solicitation**.
*Rejected:* blocking. The intent line said Buff, so I spent everything on tempo.
*Rejected:* Undercurrent, which I could not afford after Chevreuse.
This was the first turn that felt like a decision: Ethereal Spotlight is free in
energy but costs 2 Encore, and Chevreuse's member performance also costs 1 Encore,
so with 3 Encore I could have exactly one Spotlight **or** three member
performances. I took the Spotlight because the Vaporize preview was already on the
card: *"Reaction preview: Vaporize — Pyro meets Hydro: this hit deals 1.5x damage
and consumes the aura."* Chevreuse's printed number moved from 7 to 10 the moment
Spotlight resolved, and the enemy went 53 → 36, which is the 10 × 1.5 plus the
member's hit. The printed number updating in place is the single best legibility
feature I met all run.

**Turn 3** (enemy: Attack for 11, it had gained Strength 7).
Played **An Invitation** (free, fishes a random Common Companion — got Shinobu) →
**Shinobu — Grass Ring of Sanctification** → **Charlotte — First-Person Shutter** →
**Soloist's Solicitation** → **Salon Début**.
*Rejected:* Stage Presence (6 Block for 1) in favour of Charlotte (printed 6 Block
now plus 4 next turn, for the same 1 energy, and it performs a Salon member on the
way). Charlotte is strictly better here and that made the choice trivial rather
than interesting.
*Confusion I want on the record:* Shinobu printed "Gain 6 Block" and delivered 6, so
I wrote down "Spotlight does not boost Block." That was **wrong**, and I only found
out two fights later when I saw Shinobu print 4 outside a Spotlight. The card text
on screen is already the boosted number. My error, but it is the kind of error the
display invites, because nothing on the card says "this number already includes
Guest Cast" the way Applause Line says "already including Fanfare."

**Turn 4** (enemy 22 HP, Attack 11).
Played **Chevreuse** (printed 10, Vaporize on the Hydro aura) → **Undercurrent**;
the enemy died on Undercurrent.
*Rejected:* holding Undercurrent for block. I counted 15 + 1 + 5 = 21 against 22 HP,
was one short, added Undercurrent's 6 and had lethal. That arithmetic was a real
decision and the screen gave me every number I needed for it.
**Refusal #1:** my queued third card, `play "Applause Line"`, came back
`REFUSED: you are not in a battle. Forms that resolve here: choose "<reward>"; …`.
Correct behaviour — combat had ended — but recorded as instructed.

**Reward:** took **Surintendante Chevalmarin** (1 energy: a member *and* 3 Encore)
over Undercurrent, Courtroom Drama and Freminet — Shattering Pressure. Encore
starvation was already the run's binding constraint: the relic hands me a free
Ethereal Spotlight every single turn and I could almost never afford it.

---

## Fight 2 — Shrinker Beetle, HP 39/39

**Turn 1** (intent: strong Debuff, no damage).
Played **Chevreuse** → **Soloist's Solicitation** → **Regal Bearing**.
*Rejected:* Stage Presence, because nothing was incoming; I took Regal Bearing for
the same 1 energy because its Weak carries and 3 Block was as useless as 6.
This turn presented essentially no decision — five cards, one line.

**Turn 2.** The debuff landed: *"Shrink -1 — While Shrinker Beetle is alive, your
Attacks deal 30% less damage."* Every damage number on every card in hand
immediately re-printed lower (Applause Line 3 → 2, Soloist 6 → 4). That is good.
What is not good: **Charlotte's Block also fell, from 6 to 4**, on a debuff whose
printed text says *Attacks*. (I later worked out the innocent explanation — 4 is
Charlotte's unspotlighted base and the 6 I remembered was a Guest Cast number — but
from inside the fight the screen read as a debuff doing something its own text
denies.)
Played **An Invitation** (got Freminet — Pressurized Floe: Backstroke) →
**Freminet** → **Soloist's Solicitation** → **Applause Line**.
*Rejected:* Overflowing Hospitality's engine turn. Shrink is a race clock — it only
ends when the beetle dies — so building a Salon that pays out in three turns was
worse than 13 damage now. That was a genuinely interesting trade and the debuff
text is what made it legible.

**Turn 3** (enemy 13 HP, intent Attack 13; my hand had 3 total damage in it).
Played **Surintendante Chevalmarin** → **Ethereal Spotlight** → **Charlotte** →
**Salon Début**.
*Rejected:* Aria of Recompense (+5 Encore). I wanted the second member on stage more
than the fuel, since members only ever act when a Companion card performs them.
*Rejected:* the alternative "keep 2 Encore, skip Spotlight" line, which gives 4 Block
instead of 6 — I paid 2 Encore for +2 Block and one more member performance, which
in hindsight was close to a coin flip.

**Turn 4.** Enemy at 6. Played **Chevreuse** (printed 10, Vaporize) and it died.
*Rejected:* Freminet (2 energy, 10 damage + 6 Block) — same kill for twice the cost.

**Reward:** took **Flood of Emotion** — 14 damage for 1 energy — over Casting Call,
Mademoiselle Crabaletta and Sayu. It is the largest number-per-energy I had seen and
it is typed **skill**, which I flagged mentally as odd and which mattered later
(Slow and Vulnerable are worded for Attacks).

---

## Fight 3 — Leaf Slime (S) 14, Leaf Slime (M) 33, Twig Slime (S) 11

**Turn 1.** Played **An Invitation** (got Barbara — Let the Show Begin♪) →
**Chevreuse** on Twig Slime → **Soloist's** on Twig Slime (killed it) →
**Barbara**.
*Rejected:* focusing the 14 HP Leaf Slime, since 7 + 6 = 13 was one short of killing
it and killing the only attacker outright was worth more than a wounded slime.
*Deliberate probe:* I played Barbara specifically because it says "Gain 4 Burst
Energy," to see the meter move. **It did not.** After Barbara resolved there was no
Burst line in the state block at all, and the next turn's card tooltips still read
"You hold 0 of 70 Burst Energy."

**Turn 2.** Played **Flood of Emotion** on Leaf Slime (S), killing it exactly, then
**Overflowing Hospitality** (again the unexplained 1 damage: 33 → 32).
*Rejected:* Flood on the 33 HP slime plus Undercurrent, which deals 6 more total
damage but leaves two enemies alive and two status cards a turn coming at me.
*Nice screen:* Overflowing Hospitality printed *"Reaction preview: Vaporize — This
card deals no damage. Pyro plus Hydro is still consumed, and there is no hit here
for the 1.5x to multiply."* That is the tooltip refusing to flatter itself, and it
is exactly what a blind reader needs.

**Turn 3.** Played **Surintendante Chevalmarin** → **Aria of Recompense** →
**Soloist's** → **Applause Line**.
*Rejected:* Stage Presence — nothing was incoming.

**Turn 4.** Hand arrived as four **Slimed** statuses plus Ethereal Spotlight plus
Barbara. Played **Ethereal Spotlight** → **Barbara** (9 Block, and it performed
Chevalmarin for 2) → **Applause Line** → **Slimed** (1 energy, draw 1).
*Rejected:* nothing, really — this was the hand playing itself.

**Turn 5.** Hand had **no attack at all**: Spotlight, Slimed, Regal Bearing, Aria,
Stage Presence, Charlotte. Played **Slimed** to dig, drew Undercurrent, played
**Undercurrent**.
*Rejected:* Charlotte + Aria (2 damage via a member performance) for Undercurrent's
6. The finding here is the hand, not the choice: a five-card Furina hand can contain
zero ways to hurt anything.

**Turn 6.** Played **Flood of Emotion**; the slime died.
**Reward:** took **House Call** (6 damage, +2 per Salon member) over Gentilhomme
Usher, Duet and Bennett. Duet ("the next Companion card you play this turn is played
an extra time") was the one I most wanted to *see* work, but my deck's damage was
thin and House Call reads its scaling live on the card.

---

## Fight 4 — Cubex Construct, HP 65/65 (Artifact 1)

**Turn 1** (intent Buff). Played **Flood of Emotion** → **Soloist's** →
**Surintendante Chevalmarin**.
*Rejected:* Charlotte's block, since nothing was incoming.

**Turn 2** (intent Attack 9 + Buff; it was gaining Strength every turn).
Played **An Invitation** (got Shinobu, printed 4 Block this time — the correction to
my turn-3 error in fight 1) → **Ethereal Spotlight** → **Chevreuse** →
**Shinobu** → **Stage Presence** → **Salon Début**. 12 Block against a 9 attack.
*Rejected:* Aria of Recompense for Salon Début — I wanted the third body on stage
because House Call and the "full stage bows its OLDEST member out" clause both scale
on it. I never got to see a full-stage Evoke all run; the stage never filled.

**Turn 3** (enemy 25, Strength 4, hitting 11).
Played **Applause Line** → **Soloist's** → **Undercurrent** — 16 damage, no block,
took 11.
*Rejected:* Applause + Soloist + Stage Presence (10 damage, take 5). I chose the race
because the enemy's Strength climbs 2 a turn, so every extra round costs more than
the 6 HP the block saves. This was one of the better decisions the kit offered me,
and the reason it was a decision is that "Strength 2 → 4 → 6" was printed plainly.

**Turn 4.** **House Call** printed 10 ("You have 2 on stage: +4 damage, already
counted in the number above") against 9 HP and killed it.
**Reward:** took **Deep Breath** ("Choose one: Gain 1 Energy and 2 Encore | Spend 3
Encore: draw 3 cards") over The House Holds Its Breath, An Invitation and Sucrose,
because a modal card is the only card in the pool so far that asks me a question when
I play it.

---

## Fight 5 — Mawler, HP 72/72

**Turn 1.** Played **Surintendante Chevalmarin** → **Stage Presence** →
**Regal Bearing** → **Applause Line**. Full block against a 4×2.
*Rejected:* Aria for Chevalmarin — member plus Encore beats Encore alone.

**Turn 2** (intent Debuff, no damage). Played **Deep Breath** →
**An Invitation** → **Ethereal Spotlight** → **Chevreuse** (Vaporize) →
**Soloist's** → **Charlotte**.
Deep Breath's overlay was the round's most interesting screen: *"Choose a card"* with
both modes offered. It is a real choice — energy-and-fuel now, or three cards for the
Encore I rarely have. I took energy every single time I played it, and on two later
plays the overlay printed **only one option**, because I had under 3 Encore and the
draw mode was filtered out. A "choose one" that regularly has one choice is worth
knowing about.

**Turn 3** (enemy 43, intent **Attack 21**).
Played **Flood of Emotion** → **House Call** → **Soloist's** — 28 damage, no block,
took 15.
*Rejected:* using the Vulnerable Potion. I worked out that with 3 Vulnerable my 28
became about 42 against 43 HP — one short of lethal — and since I was going to eat
the 21 either way, the potion bought nothing. Making that call needed the printed
Vulnerable text and the printed HP; both were there.

**Turn 4.** Enemy 15, hitting 6×2. Played **Undercurrent** → **Applause Line** →
**Stage Presence**.
*Rejected:* Regal Bearing's Weak+3 Block versus Stage Presence's 6 — identical
mitigation this turn, so I took the simpler one.

**Turn 5.** **House Call** for 8 against 6 HP, dead.
**Reward:** took **Razor — Lightning Fang** ("For 2 turns, your Attacks apply Electro
and deal 3 additional damage") over Commanding Gaze, Blocking Notes and Breathless.

---

## Elite 1 — Phrog Parasite, HP 62/62 (Infested 4), then 4 Wrigglers

**Turn 1.** Played **Razor**, and **Undercurrent's card text changed in my hand from
"Deal 2 damage to ALL enemies 3 times" to "Deal 5 damage to ALL enemies 3 times."**
That is the clearest thing the kit did all run: a buff whose effect I could read off
the card before committing. Played **Undercurrent** for 15.
*Rejected:* Flood (14) + Undercurrent (6) for 20 flat, because Razor also covers next
turn.

**Turn 2** (enemy 47, hitting 4×4).
Played **Chevreuse** (printed 10 with Razor, and a *"Reaction preview: Overloaded —
Pyro meets Electro: 6 damage to ALL enemies and 1 Weak on the reacted enemy"*) →
**Soloist's** → **Applause Line** → **Stage Presence**.
**Where the screen and the outcome disagreed.** The four cards printed 10 + 6 (the
Overloaded rider) + 9 + 6 = 31. The enemy went 47 → 22, i.e. **25**. And the Weak
never appeared on the enemy, nor in the damage I took: I had 6 Block against a
printed 16, and I lost exactly 10 HP, which is 16 − 6 with no Weak anywhere in it. I
could not tell from the screen whether Overloaded fired at all; the Electro aura was
still showing afterwards, but my own Razor-fuelled attacks re-apply Electro, so the
aura proves nothing either way. (I got a cleaner reading later — see the boss and
elite 3 notes.)

**Turn 3** (enemy 22, giving statuses). Played **Deep Breath** → **An Invitation**
(got Kujou Sara — Crowfeather Cover) → **Ethereal Spotlight** → **Kujou Sara** →
**House Call** → **Charlotte** → **Regal Bearing**.
*Rejected:* using the Vulnerable Potion into Artifact 1, which would have eaten it.
*Second disagreement:* Guest Cast was up and Sara says "Your next Attack deals 4
additional damage." House Call's 6 plus a spotlighted 4 should be 12; I saw exactly
**10**, i.e. Sara's rider paid 4, not 6. So "printed damage" for the 50% apparently
means the card's own damage line and not a rider it grants — which is defensible, and
completely unstated.
Regal Bearing's Weak *did* land and printed as `Weak 1 (debuff)` on the enemy, which
is what let me conclude the Overloaded Weak earlier had genuinely not landed.

**Turn 4.** **Salon Début** → **Stage Presence** → **Flood of Emotion** killed the
Parasite, and Infested spawned **four Wrigglers** (18/19/21/17), all Stunned.

**Wriggler turns 5–9,** compressed, because they were mostly arithmetic:
- r5: **Undercurrent** (6 to all) + **Applause Line** + **Stage Presence**. Two
  **Infection** statuses in hand — "Unplayable. At the end of your turn, if this is
  in your Hand, take 3 damage" — 6 unavoidable damage. Nothing died. *Rejected:* the
  Vulnerable Potion, which I checked and it still did not reach a kill.
- r6: **Chevreuse** killed one; **House Call** + **Soloist's** killed a second. This
  was the best turn of the run: two attackers removed exactly, 3 energy, and the
  screen gave me all four HP totals to plan it.
- r7: no attacks in hand at 19 HP. **Chevalmarin** → **Regal Bearing** (Weak) →
  **Charlotte**. Nine Block against 16. *Rejected:* nothing; there was nothing else.
- r8: at 10 HP with **three** Infections in hand (9 damage) and both enemies buffing.
  **Charlotte** for 6 more Block so the Infections hit block instead of me, plus
  **Applause Line**. The choice of "block a card that damages me from inside my own
  hand" was a real one.
- r9: **Undercurrent** killed one and left the other on 1; **Chevreuse** finished it.
  Note the naming: I typed `Wriggler (2)` and the tool answered `WRIGGLER_0` /
  "Wriggler", because the numbering had re-counted when the first one died. The
  bridge warns about this in its own boilerplate and the warning is earned.

**Rewards:** Snecko Skull; took **Courtroom Drama** ("The first Elemental Reaction
you trigger each turn applies 1 Vulnerable and 1 Weak to its target") over Macaron
Break, Dramatic Entrance and Charlotte — Framing, betting on a single-target boss.

---

## Elite 2 — Bygone Effigy, HP 127/127

Its debuff read *"Slow 0 — Whenever you play a card, this enemy receives 10% more
damage from Attacks this turn,"* and crucially the line updated to
**"Slow 30 … (Receives 30% more damage)"** as I played. That turned every turn into
an ordering puzzle: cheap non-attacks first, attacks last. It is the single most
decision-dense enemy I met, and none of that came from Furina's kit — it came from
the enemy's printed rule.

**Turn 1.** **Chevalmarin** → **Salon Début** → **House Call** last: 15 damage.
**Turn 2.** **An Invitation** (Thoma) → **Ethereal Spotlight** → **Deep Breath** →
**Charlotte** → **Flood of Emotion** → **Soloist's** last: 30 damage.
*Rejected:* Thoma's 7 Block, since the Effigy was buffing and I wanted the Slow
stacks spent on damage.
**Turn 3** (enemy 82, Strength 10, hitting 23; me at 44).
Used the **Vulnerable Potion**, then **Razor** → **Undercurrent**: 27 damage.
*Rejected:* Stage Presence + Undercurrent (7 damage, 12 Block). I judged the fight
unwinnable on the block plan — 23 rising per turn against 6-Block cards — so I raced.
Poison 5 appeared on the enemy here and I never found the printed source for it.
**Turn 4.** **Courtroom Drama** → **Chevreuse** → **Applause Line** →
**Stage Presence**: enemy 50 → 16, and this time the enemy visibly gained
`Vulnerable 3` and `Weak 1` and `Poison 9`. Courtroom Drama's rider clearly fired.
**Turn 5.** **Flood of Emotion** finished it from 7.

**Rewards:** Powdered Demise, Vexing Puzzlebox; took **Crescendo** ("Deal 6 damage,
already including Fanfare. Permanently increase this card's damage by 2 this
combat," +1 per **2** Fanfare) over Macaron Break, Lasting Impression and Freminet.
The tighter Fanfare ratio is the thing: Applause Line's +1 per 4 Fanfare never once
mattered, +1 per 2 did.

**Shop** (287 gold): bought **High Tide**, **Crashing Waves**, **Poison Potion**,
**Flex Potion**; skipped Card Removal, Grand Gala (157, adds four members at once)
and Twisted Funnel (205). Molten Egg — picked up later — silently upgraded the two
attacks I had already bought, which is why High Tide printed 19 and then 23 rather
than 15 in the boss fight.

---

## Elite 3 — Byrdonis, HP 81/81 (Territorial: +1 Strength each of its turns)

I walked in at **16/92** on a forced path, against a 17-damage opener, with exactly
one Block card in hand. This is the only fight where I emptied the belt.

**Turn 1.** **Powdered Demise** → **Poison Potion** → **Flex Potion** → **Deep
Breath** → **Razor** → **House Call** → **Crescendo** → **Stage Presence**: 28 from
cards, and Snecko Skull turned the 6 Poison into 7. Enemy 81 → 53. Took 11, down to
7 HP, because 6 Block was all the hand had.
*Rejected:* saving the potions for the boss. At 16 HP against 17, saving anything for
a boss I might not reach was not a real option, and the potions are what won this.

**Turn 2** (enemy 37 with Poison 6 and Demise 9; me at 7 HP against a 4×3).
Played **Chevreuse** first and watched carefully, because I wanted a clean reading on
Overloaded: the card printed 10, showed *"Reaction preview: Overloaded"*, and the
enemy went **37 → 27**. Ten. **The 6 AoE damage did not happen, and no Weak was
applied** — and the Electro aura afterwards read `2`, i.e. refreshed rather than
consumed. Two independent sightings now say Chevreuse's previewed Overloaded does
not resolve.
Then **Undercurrent** (15) and **Applause Line** (6) put it on exactly **6** with
**Poison 6** on it.
*Rejected:* the safe-looking line (Flood 14 + Applause + Charlotte's 4 Block), which
I computed leaves the enemy at 1 after poison, alive, swinging 12 into my 7 HP with 4
Block — dead. The line I took kills it with poison at the start of its turn, before
it acts. That was the best decision of the run and I could only make it because the
poison tooltip says *"At the start of its turn"* rather than just "each turn."
It worked; the fight ended on my end-turn.

**Rewards:** Explosive Ampoule, Molten Egg; took **Thunderous Ovation** (6 Block, +1
per 2 Fanfare) over Blocking Notes, Commanding Gaze and an upgraded
Chevreuse — Ring of Bursting Grenades+ (12 to ALL for 2). At 7 HP I bought defence.

**Slippery Bridge event:** chose **Overcome** (remove House Call) over **Hold On**
(lose 3 HP to reroll the card). At 7 HP, paying 3 HP for a reroll that might offer up
High Tide or Flood was a worse gamble than losing a mid-tier attack.

---

## Fight — Boss: Vantom, HP 173/173

Its opening buff is *"Slippery 8 — The next 8 times Vantom loses HP, it only loses 1
HP instead."* That is a genuinely good puzzle and it is aimed squarely at this kit:
the answer is many small hits, and Furina has Undercurrent (3 hits), Applause Line,
and Salon members whose performances each count as a hit.

**Turn 1** (Slippery 8, attack 7). **Top Billing** (free from Vexing Puzzlebox) →
**Overflowing Hospitality** → **Thunderous Ovation**.
*Rejected:* Flood of Emotion and Chevreuse — spending a 14 into Slippery would have
bought 1 damage. Holding the big cards while stripping stacks is the correct play and
the Slippery counter made it obvious.

**Turn 2.** **Ethereal Spotlight** → **Charlotte** → **Crescendo** →
**Crashing Waves**: three stacks stripped, Slippery 7 → 4, 7 Block.
*Deliberate:* Crescendo into Slippery still deals 1 but still gets its permanent +2,
so it was the cheapest possible stack to spend. That is a real bit of kit texture.

**Turn 3** (attack **26**, me at 29). **An Invitation** (Gorou) → **Applause Line**
→ **Regal Bearing** → **Gorou — General's War Banner** → **Stage Presence**: 16 Block
plus Weak, Slippery to 2, took 2.

**Turn 4** (enemy buffing). Two **Soloist's** to burn the last two Slippery stacks,
then **High Tide** for 19 at full value.
*Rejected:* leading with High Tide, which Slippery would have eaten for 1.

**Turn 5.** No attacks in hand. **Deep Breath** → **Ethereal Spotlight** →
**Courtroom Drama** → **Gorou** → **Razor**, banking a 13-Block Companion and two
riders for the following turn. Took 0.

**Turn 6.** **High Tide** (23) → **Crescendo** (16) → **Flood of Emotion** (14).
**The second big screen-vs-outcome gap:** those cards print **53**, and Vantom went
**145 → 61**, i.e. **84**. Poison 9 also appeared on it with no printed source I could
find. I never worked out where the extra 31 came from — Courtroom Drama's Vulnerable
is the obvious suspect, but nothing on any screen told me a reaction had triggered,
and the enemy's aura history does not obviously support it. It went in my favour, but
it is the same class of defect as the Overloaded one: the numbers on the cards do not
add up to the number on the enemy.

**Turn 7** (enemy 61, attack **28**, me at 15). **Thunderous Ovation** (8) →
**Stage Presence** (6) → **Crashing Waves** → **Applause Line** →
**Explosive Ampoule**. 14 Block against 28 left me on exactly **1 HP**.
*Rejected:* any line that traded block for damage; 28 into 15 is lethal and the
intent number said so.

**Turn 8** (enemy 30, intent **Buff** — the free turn that saved the run). Two
**Soloist's** plus **Regal Bearing**; poison took it to 10.

**Turn 9.** **Chevreuse** printed 12 against 10 HP. Vantom died. Final: **1/92**.

**Reward:** took **Showstopper+** (15 damage for 1, "If it kills: gain 6 Encore and
draw 2 cards") over The Final Verdict+, The Sea Is My Stage and Navia. Worth noting
that The Final Verdict+ prints, in the reward list, *"Deal 0 damage, already
including Fanfare"* — the scaling clause is +1 per 1 Fanfare and I held none, so the
card correctly advertised itself as doing nothing. I found that funny and also
exactly right.

Then: 100 Gold, Radiant Tincture, **proceed** → the act-2 map (boss: Kaiser Crab).
Stopped there.

---

## The kit, after 9 fights

### (a) Which decisions felt like real choices, and what they traded off

Four, and only four, recurred:

1. **Ethereal Spotlight's price.** The relic hands me a free Spotlight every turn and
   it costs 2 Encore, while every Salon member performance costs 1 Encore. So the
   question "do I buy 50% on my Companions, or do I buy two member performances?" is
   live on most turns, and both sides are visible. This is the best-designed tension
   in the kit. It is also the one that most often resolves to "I have 0 Encore, the
   card is greyed out, there is no choice" — which is how it went for most of fights
   1, 2, 4 and 5.
2. **Race or block**, sharpened by the enemies rather than by Furina. Shrinker
   Beetle's Shrink ("while it is alive, your Attacks deal 30% less"), Cubex's climbing
   Strength, and Byrdonis's Territorial all make "kill it a turn sooner" purchasable
   in HP, and the numbers to price it are all on screen.
3. **Reaction setup.** Deciding to lead with a Hydro card so Chevreuse's Pyro
   Vaporizes, or to eat the aura with Razor's Electro instead, is a genuine
   sequencing choice, and the *"Reaction preview:"* line on the card is what makes it
   playable blind. It is undermined by (c) below.
4. **Ordering against a printed multiplier.** Bygone Effigy's Slow and Vantom's
   Slippery both turned a turn into "which order, and which card do I waste on the
   cheap stack?" Crescendo-into-Slippery (deal 1, keep the permanent +2) was the most
   satisfying single play of the run.

Note what is *not* on that list: the Salon. Deciding which member to field never came
up, because Salon Début is random and I never once filled the stage to three and got
the Evoke payout the tooltip spends four lines describing.

### (b) What felt automatic, and what never seemed worth playing

- **Automatic:** every turn where the hand contained one attack and two Block cards,
  which was most turns in fights 1–5. Also automatic: Stage Presence, Regal Bearing
  and Soloist's Solicitation, which are 1-energy cards with no rider and no scaling —
  you play them when you have spare energy and there is nothing to think about.
- **Never worth playing:** **Aria of Recompense** (1 energy for 5 Encore) was close
  to dead. Encore only buys member performances and Spotlights, and I could not
  reliably convert 5 Encore into 5 anything. **Applause Line**'s Fanfare clause is
  +1 per **4** Fanfare and I held 0–8 Fanfare all run, so its scaling produced +0 or
  +1 essentially always — it is a 3-damage card wearing a scaling costume. Compare
  Crescendo and High Tide at +1 per **2**, which visibly moved.
- **Fanfare in general felt like a stat I watched rather than used.** Its own tooltip
  says "Cards read it; nothing spends it," it decays 20% a turn, and across nine
  fights it ranged 0–8. Flood of Emotion's "If you have at least 20 Fanfare" clause
  and Dramatic Entrance's "at least 12" never came within reach. I do not know what a
  Fanfare deck looks like, and I played nine fights.

### (c) What I could not understand, or that seemed to contradict its own printed text

Five things, roughly in order of how much they cost me:

1. **Burst Energy does not exist.** Every relevant card carries a nine-line tooltip
   about a 70-point meter that fills and drops a Burst card into my hand. I played
   "Burst +5" cards at least eight times and Barbara's explicit "Gain 4 Burst Energy"
   twice. Every subsequent screen said **"You hold 0 of 70 Burst Energy,"** and no
   Burst line ever appeared in the state block. Either the meter is broken or it is
   unreachable in act 1; from inside, it reads as a large, prominent, load-bearing
   mechanic that is simply not connected.
2. **The Salon keyword and the Salon Member buff contradict each other outright.**
   The keyword on every Salon card says *"Members do NOT act on their own. A Companion
   card you play performs the front member."* The buff in my own state block says
   *"At the start of your turn, each Salon Member spends 1 Encore for its act."* I
   tested it on fight 1 turn 2: Encore did not move and no damage happened at turn
   start. The keyword is right and the buff is wrong, and the buff is the text sitting
   in the status bar all fight.
3. **Chevreuse's previewed Overloaded does not resolve.** Twice, on a card printing
   *"Reaction preview: Overloaded — 6 damage to ALL enemies and 1 Weak,"* the enemy
   lost exactly the card's printed damage and no more, gained no Weak, and kept an
   Electro aura. The cleanest reading is elite 3 turn 2: printed 10, enemy 37 → 27,
   no Weak. Vaporize, by contrast, demonstrably worked (Chevreuse 10 → 15 on a Hydro
   aura in fight 1).
4. **Numbers that do not add up in the other direction.** Boss turn 6: three cards
   printing 53 removed 84 HP, and a Poison 9 appeared with no printed source. Elite 2
   turn 3 likewise sprouted Poison 5 from nowhere I could see. I would rather be
   over-rewarded than under-, but I could not audit either.
5. **Overflowing Hospitality deals 1 unprinted damage** every time. Small, consistent,
   and it means the card silently strips a Slippery stack — which is actually useful,
   and which nothing tells you.

Lesser confusions: the state block sprouts **"Spotlight Mode: 2 / Spotlight Moved: 1
/ Spotlight Plays: 1"** with the disclaimer that the feed carries "no rule for how it
is spent," and these appear and vanish between screens; I never learned what any of
them meant, and Director's Cut (seen at Neow) reads "If you moved the Spotlight this
turn," so there is evidently a whole Spotlight-position subsystem I never saw a
handle for. Charlotte's delayed Block leg prints 4 and delivers 6 under Guest Cast,
so the *immediate* leg shows its boost and the *delayed* leg does not. And Kujou
Sara's granted rider does not take the Spotlight multiplier even though Sara is a
Companion.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted:** **Aria of Recompense**. One energy, five Encore, and Encore has
  almost nothing to buy — it is the fuel card for an engine I could never get running.
  Runner-up: Applause Line, for reasons in (b).
- **Happiest to draw:** **High Tide** (bought, and silently upgraded by Molten Egg) —
  23 damage for 1 energy by the boss. But the more interesting answer is
  **Crescendo**: it printed 6 in the shop and 16 by the boss's sixth round, and
  watching the number climb on the card in my hand — from its own +2, from Fanfare —
  was the only time this kit made me feel like something was compounding. If Furina is
  meant to build to something, Crescendo is the card that told me so.

### (e) Did the first turn of the first fight already present a decision?

**A small one, yes — and mostly by accident.** Turn 1 of fight 1 gave me 3 energy and
six cards, and I really did choose Overflowing Hospitality (2 energy: a member, 3
Encore, an aura) over Undercurrent (2 energy: 6 damage), which is a build-versus-tempo
question with both sides printed. But the rest of the turn played itself — Applause
Line is free, Stage Presence is the only 1-energy sink — and the one card that looked
like it was asking me something, Ethereal Spotlight, was greyed out with
*"CANNOT BE PLAYED: you have no Encore, and this costs 2."* So: a decision existed,
it was the second-cheapest kind (which two-drop), and the kit's signature resource
was inert on the turn it was introduced.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed ones:
- `mkdir -p "<scratchpad>/furina-r2run2" && echo ok` — one call, at the start. I then
  never used the directory; I kept no notes file and reasoned from the `observe`
  output in the transcript.
- I piped `observe` through `sed -n '<ranges>'` on most calls to re-read a slice of
  the screen (hand only, enemies only, state block only) rather than re-print the
  whole page. This is the "piping an `observe` through `sed`" the brief permits. No
  other filtering, and I never suppressed output I then acted on without reading it —
  where I used `>/dev/null` it was on `act` calls whose result I read on the next
  `observe`.

Tools used: **Bash** (for every `observe` / `act` / `sed` / `mkdir` above) and
**Write** (once, for this record). No Read, no Grep, no Glob, no Agent, no other
understudy subcommand. I did not run `harness state`, `scenario`, `staged_turn`,
`soak`, or anything else.

Refusals encountered: **one**, recorded in fight 1 — `play "Applause Line"` returned
`REFUSED: you are not in a battle. Forms that resolve here: choose "<reward>"; choose
<number> …`, because the fight had already ended on the previous card. Never three in
a row. No `TOOL-BLOCKED` and no `REFUSED: …leak…` at any point. Two `choose` calls
(both on Deep Breath's modal, elite 1 and elite 3) produced no output and appeared not
to register; I re-issued them and they were accepted, and I have counted both attempts
in the action estimate rather than only the successful ones.

Budget caveat, restated because it belongs here as much as in Identity: **I exceeded
`--max-actions 250`,** finishing at roughly 290 accepted actions. I was not tracking a
counter, nothing in the loop told me, and I discovered it only while writing this
section. The run's stop condition was reached on its own terms, but the last stretch —
about the boss fight from round 2 onward — was played past the cap.
