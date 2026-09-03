# KLEEMOD-KOKOMI — blind seat, lane 1, act 1

## Identity

- **Model / seat:** Claude Opus 5 (1M), blind TESTER seat, lane 1.
- **Character:** the Bake-Kurage / Plan kit. The screen never printed a character
  name on any page I saw. The only place a name appeared at all was a status line
  in round 4 of two fights: `Kokomi Burst: 5/20`. So I am inferring "Kokomi" from
  that meter, not from a title.
- **Run seed:** never printed. No screen I saw carried a seed.
- **Act:** act 1. The map printed `At the top of this act: **Waterfall Giant**`.
  I did not reach it.
- **Actions accepted:** 121 accepted `act` calls, 1 refused (my own tally, kept
  by hand as I went; nothing on screen counts them).
- **Termination reason:** act budget. I stopped on the map screen, 5 floors from
  the boss, with ~9 accepted acts of headroom left, because the shortest route to
  the boss is 5 more rooms (at least two of them fights) and starting a fight I
  could not finish would hand the next seat a half-played combat instead of a
  clean map.
- **Where the run stands:** the map, act 1, after the second rest site. Next
  nodes offered: `Unknown (path 1)` (leads on to Monster) and `Shop (path 2)`
  (leads on to Monster). Floors ahead as printed: 1 = Elite, Unknown, Shop,
  Elite, Unknown; 2 = Unknown, Monster, Monster; 3 = Elite, Unknown, Monster;
  4 = RestSite, RestSite, RestSite; 5 = Boss.
- **HP:** 44/80. Trajectory: start 64/80 → 58 (fight 1) → 43 (fight 2) → 30
  (fight 3) → 28 (fight 4) → **rest 52** → 22 (elite) → **rest 46** → 44
  (fight 6) → 44 now.
- **Gold:** not printed anywhere after the shop. Last printed figure was
  `You have 99 gold.` at the shop; I spent 78 there, and picked up 16 + 43 + 14
  in later rewards. By arithmetic that is 94, but no screen said so.
- **Potions:** none held. One was found and spent (Heart of Iron, in fight 4).

**Relics, exactly as printed:**

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy. Card rewards after a fight offer a fourth Companion choice.
- **Scroll Boxes** — Upon pickup, choose 1 of 2 packs of cards to add to your Deck.
- **Stone Cracker** — At the start of each combat, Upgrade 2 random cards in your Draw Pile for the rest of combat.
- **Anchor** — Start each combat with 10 Block.

**Deck, exactly as printed** (from the Smith screen at the last rest site, before
I upgraded Kurage's Oath; 20 cards):

- **Strike ×4** — cost 1, attack — Deal 6 damage.
- **Defend ×4** — cost 1, skill — Gain 5 Block.
- **Kurage's Oath (proto)+** (upgraded) — cost 1, skill — Play on the Bake-Kurage. Plan: Deal 10 damage to ALL enemies.  *(was "Deal 7 damage to ALL enemies" before I smithed it)*
- **Slack Water (proto)** [Hydro] — cost 1, attack — Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- **Feint** [Hydro] — cost 1, attack — Deal 6 damage. Plan: Deal 10 damage.
- **Deep Current** [Hydro] — cost 1, attack — Deal 6 damage to ALL enemies.
- **War Council** — cost 1, skill — Play on the Bake-Kurage. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- **Stolen Chapter (proto)** — cost 1, skill — Draw 2 cards. Plan: Draw 4 cards.
- **Song of Pearls (proto)** — cost 1, power — Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- **Kujou Sara — Tengu Stormcall (proto)** [Electro] — cost 1, attack — Deal 5 damage. Next turn, your Attacks deal 5 additional damage.
- **Chiori — Fluttering Hasode** — cost 1, skill — For 3 turns, at the end of your turn deal 6 Geo damage to a random enemy, ignoring Block. Exhaust.
- **Dahlia — Favonian Favor (proto)** — cost 1, skill — Gain 7 Block. Whenever an Elemental Reaction happens this turn, gain 3 Block.
- **Coral Bulwark** — cost 1, skill — Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- **Rosaria — Ravaging Confession** [Cryo] — cost 1, attack — Deal 9 damage. If the enemy has an aura, apply 1 Vulnerable.

### Neow

Offered: **Neow's Torment** (add 1 Neow's Fury to your Deck), **Scroll Boxes**
(choose 1 of 2 packs of cards to add to your Deck), **Dowsing Rod** (add 1
Dowsing to your Deck).

I picked **Scroll Boxes**, because two of the three options add one card I could
not read in advance, and this one showed me six card faces of a kit I had never
seen — the pick that buys the most information as well as the most cards.

Then, between the two bundles, I picked bundle 1 (**Feint / Deep Current /
War Council**) over bundle 2 (**Change of Plans / Sea-Salt Prayer / Moon's
Reflection**), because bundle 1 is stats — single-target, AoE, and an AoE
debuff plan — while bundle 2 is three cards that all manipulate a Plan engine
I had not yet seen a single card of; Change of Plans and Moon's Reflection are
both worth nothing until the deck already has Plans worth replaying.

---

## Fight 1: Corpse Slug 26/26 + Corpse Slug 25/25

Opening HP 64/80. Both slugs printed `Ravenous 4 (buff) — When an enemy dies,
Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength.`

**Turn 1.** Played, in order: Kurage's Oath (proto) → Bake-Kurage;
Slack Water (proto) → Bake-Kurage; Deep Current (6 to all).
I wrote two Plans deliberately to find out whether the Kurage takes more than
one, since the page said only "Nothing is planned. The morning is empty." It
does, and it says so cleanly: `Plan 2 (buff) — Carries out 2 Plans at the start
of your next turn, in order.` and a numbered list under the Bake-Kurage.
**Rejected:** playing Slack Water at a slug for 4+2 now instead of banking it.
I banked because the two slugs were at full HP and nothing I could do this turn
killed either, so tempo was worth more than 6 damage.

**Turn 2, morning.** The page printed:

```
- The Bake-Kurage carried these out at the start of this turn, front first:
  - Bake-Kurage: Kurage's Oath (proto), 7
  - Bake-Kurage: Slack Water (proto), 1
```

Matched the board exactly: 20→13 and 19→12 from the Oath's 7 AoE, then 13→11
and 12→10 from Slack Water's Weak — the 2 extra per enemy is the Tamakushi
Casket firing on the debuff. **The printed line reports only the plan's first
number.** "Slack Water (proto), 1" is the Weak stack; the 2 damage per enemy the
Casket added has no line at all. I could reconstruct it, but only because I had
the relic text in front of me and did the arithmetic.

Played: Strike, Strike into Corpse Slug (2) (10 HP) to kill it, then Strike into
the survivor. **Rejected:** Defend, which printed `Gain 3 Block` rather than 5
because I was Frail — the card face showed me the Frail-reduced number, which is
good. I rejected it because I wanted to test Ravenous: killing one slug printed
`Intent: Stunned (Stun) — This enemy can't act on its next turn.` and
`Strength 4` on the survivor. Killing a slug buys a free turn and costs you a
+4 Strength enemy. That is a real, legible trade and I used it again in fight 4.

**Turn 3.** Slug at 5 HP, one Strike. **No rejected alternative — this turn
presented no decision.**

---

## Fight 2: Seapunk 46/46

**Turn 1.** Deep Current (6), Strike, Strike = 18. **Rejected:** Stolen Chapter
as a Plan (Draw 4 next morning). I worked out it was strictly a wash — playing
it now draws 2 and leaves the same 2 energy, planning it draws 4 but next turn I
still only have 3 energy and would be energy-limited, not card-limited. That is
a real finding about the card: **Stolen Chapter's Plan is only better than its
face when you have 0-cost cards or spare energy, and this deck has neither.**

**Turn 2.** Kurage's Oath → Bake-Kurage; Slack Water at Seapunk; Strike.
**Rejected:** Slack Water as a Plan. Its Plan line is "Apply 1 Weak to ALL
enemies" — no damage — against a single enemy, whereas playing it at the face
does 4 + 2 (Casket) = 6, the same as a Strike, *and* applies the Weak now, in
time to cut the incoming hit. **Slack Water's Plan line is worse than its own
face against one enemy, and the card does not say so.**

**Turn 3, morning.** `Bake-Kurage: Kurage's Oath (proto), 7` — matched, 16→9.
Killed it with Strike + Feint. **Rejected:** Feint as a Plan (10 > 6), rejected
because the Seapunk was at 9 and would have taken a buff turn first.

---

## Fight 3: Toadpole 21/21 + Toadpole 22/22

**Turn 1.** War Council → Bake-Kurage; Strike, Strike into Toadpole (2).
**Rejected:** Defend over the second Strike — the other Toadpole was on
`Intent: Empower (Buff)` and I wanted it dead before whatever it was buying
arrived.

**Turn 2, morning.** `Bake-Kurage: War Council, 5` — board showed 21→14 and
10→3, i.e. 7 each, not 5. Same gap as fight 1: the line prints the Plan's damage
number and silently omits the Casket's 2-per-debuff. Matched what I expected,
but only because I was doing the arithmetic by hand.

What the Empower turned out to buy was `Thorns 2 (buff) — When hit by an attack,
deal 2 damage back`, which is exactly the buff that punishes the three-small-hits
deck I have. Played Deep Current (kills the 3 HP one, 14→8 on the other), then
Strike, Strike. Took 6 back off Thorns and ended the fight on the spot.
**Rejected:** Defend + two attacks, which would have left the Thorns Toadpole
alive one more turn and cost more Thorns damage than the Defend prevented.

---

## Fight 4: Corpse Slug 27/27 + Corpse Slug 25/25 + Corpse Slug 26/26

Entered at 30/80 — the tightest spot of the run. Incoming turn 1 was 6 + 8 +
a debuff.

**Turn 1.** Kurage's Oath → Bake-Kurage; War Council → Bake-Kurage; Defend;
and the potion **Heart of Iron** (`Gain 7 Plating`). **Rejected:** playing
Kujou Sara for 5 damage now. At 30 HP against 78 enemy HP the fight is not
winnable on damage this turn, so I bought the whole turn's damage as two banked
Plans and spent the third energy plus the potion on not dying.
The potion resolved as `Plating 7 (buff) — At the end of your turn, gain 7
Block. Plating is reduced by 1 at the start of your turn.` — a repeating block
source, which the reward screen's one-line "Gain 7 Plating" does not tell you.
I bought it blind and got lucky.

**Turn 2, morning.**

```
- The Bake-Kurage carried these out at the start of this turn, front first:
  - Bake-Kurage: Kurage's Oath (proto), 7
  - Bake-Kurage: War Council, 5
```

Board: 27→13, 25→11, 26→12 — 14 each, matching 7 + (5+2). Matched.

Played Slack Water into the 11 HP slug (11→5, so the Casket does fire on a
*re-applied* Weak — I had to test that before committing the kill), then Feint to
kill it. Both survivors printed Stunned + Strength 4: **killing one of three
stuns both others.** Third energy: Stolen Chapter → Bake-Kurage, because the
board was stunned so there was nothing to defend against and nothing else to
kill. **Rejected:** Defend, which would have blocked zero.

**Turn 3.** The Plan drew 4 (hand of 9, 3 energy — the first time all run the
draw mattered). Deep Current, Strike to kill the low one, Chiori — Fluttering
Hasode. **Rejected:** three attacks with no Chiori, which kills the same two
slugs; I spent the card to see what a Companion's own effect looks like on the
board.

**Turn 4.** Last slug at 1 HP with Strength 8 and a 16-damage intent. I asked
for `play "Strike (1)" on "Corpse Slug"` and was refused:

> `nothing here is called 'Strike (1)'. What is on the screen: Defend (1), Defend (2), Kujou Sara — Tengu Stormcall (proto), Kurage's Oath (proto), War Council`

That is my error, not the bridge's — I had assumed a Strike was in hand without
looking. The refusal listed the hand back, which was exactly enough to fix it.
Killed it with Kujou Sara.

**Where the screen and the outcome disagreed.** This is the fight where
`Kokomi Burst: 5/20 — the game's data feed carries this meter's amount and its
maximum, and no rule for how it is spent` first appeared, in round 4. It had not
been on the page in rounds 1–3. No card in my deck, no relic, and no keyword
box mentions a Burst, a meter, or how it fills. I finished the act without ever
learning what it is or being able to spend it.

---

## Fight 5 (Elite): Skulking Colony 75/75

`Hardened Shell 20 (buff) — Skulking Colony cannot lose more than 20 HP each
turn.` Entered at 52/80.

**Turn 1.** Dahlia — Favonian Favor (7 Block), Deep Current, Strike = 12 damage.
**Rejected:** two Defends and Dahlia (17 block, 0 damage) — 75 HP behind a
per-turn cap means the fight is a fixed number of turns and pure turtling
never ends it.

**Turn 2.** Slack Water at the Colony, Strike, Strike = 18. **Rejected:** a
Defend in place of a Strike. Slack Water is worth more than a Strike here — 4 + 2
Casket is the same 6, and the Weak cut the Colony's 14 to 10 — so the defensive
card *was* the attack. That is the nicest small decision the kit gave me.

**Turn 3.** Chiori; Kurage's Oath → Bake-Kurage; War Council → Bake-Kurage.
**Rejected:** Song of Pearls and a Defend. I chose to fill next morning to the
cap: 7 + 7 planned, plus Chiori's 6 at end of turn, is exactly 20.

**Turn 4 — the turn where the screen taught me something I had got wrong.**
Morning printed 7 + 5 as before; the Colony sat at 25 and its power now read:

> `Hardened Shell 6 (buff) — Skulking Colony cannot lose more than 20 HP each turn.`

**The number and the sentence contradict each other on the same line.** I played
Kujou Sara (5 damage) and the Colony went 25 → 19, and Hardened Shell went 6 → 0.
So the printed *number* is the HP it may still lose this turn, and the printed
*text* is the per-turn maximum, and nothing on the page says the number means
that. Working it out gave me the real rule, which is the sharpest thing I learned
all act: **the Bake-Kurage's morning damage lands inside the same turn window as
your cards, so a Plan and a hand both draw down one 20-HP allowance.** I had
been treating banked damage as free extra damage; against a cap it is not.

Having read `Hardened Shell 0`, I stopped attacking. Played Feint →
Bake-Kurage (banking 10 into next turn's fresh allowance) and Slack Water at the
Colony purely for the Weak. Slack Water dealt exactly 0 — 19 → 19 — and Weak
still went 1 → 2. **Damage is capped; debuffs still land.** The Casket's 2 was
swallowed by the cap too.

**Rejected**, and this is the decision I am happiest with all act: Feint and
Slack Water at the enemy's face, which is what I would have played if I had not
noticed the 0 and which would have done literally nothing.

Kujou Sara into a Hydro aura also produced the one Elemental Reaction of the
run. Her card face grew a contextual line the moment the target had an aura:

> `*Reaction preview: Electro-Charged* — This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect.`

The board then showed `Poison 4 (debuff) — At the start of its turn, loses 4 HP,
then reduce Poison by 1.` The preview promised "a 4-damage decaying
damage-over-time effect" and the board delivered a thing called Poison. Same
mechanic, two names; I had to guess they were the same thing.

**Turn 5.** `Bake-Kurage: Feint, 10` — 19 → 9, then Poison → 5. One Strike ended
it. **No rejected alternative — this turn presented no decision.**

---

## Fight 6: Calcified Cultist 38/38 + Damp Cultist 51/51

**Turn 1.** Both enemies on `Intent: Empower (Buff)` — zero incoming — so:
Song of Pearls (the power), Kurage's Oath → Bake-Kurage, Strike.
**Rejected:** the two Defends in hand, which would have blocked nothing. A
free turn is where a power goes, and the kit gave me one legibly, because the
intent line told me nothing was coming.

**Turn 2.** The Empower resolved into `Ritual 2` on one and `Ritual 5` on the
other — +5 Strength a turn, a clock. Played Coral Bulwark+ (9 Block),
Chiori, Kujou Sara at the Damp Cultist. **Rejected:** Dahlia for block instead
of Kujou Sara — I took the reaction and the +5 rider because Ritual 5 means
every turn I spend not killing costs more than the last.

Stone Cracker's two random in-combat upgrades showed up here and are handled
well: my hand printed **Coral Bulwark+ (upgraded)** and **Deep Current+
(upgraded)** with their real numbers, not a tag.

**Turn 3.** The +5 rider resolved as `Fantastic Voyage 5 (buff) — Your Attacks
deal 5 more damage this turn.` and — this is the best legibility in the whole
kit — **every card in hand reprinted its own number with the buff baked in**:
Strike read `Deal 11 damage`, Slack Water `Deal 9 damage`, Feint
`Deal 11 damage. Plan: Deal 10 damage.` Note that last one: the face went up to
11 and the Plan line stayed at 10, which quietly told me the buff will not be
there in the morning. I did not have to guess.

Played Strike (11) + Slack Water (9+2) to kill the Calcified Cultist exactly,
then Feint at the Damp Cultist. **Rejected:** Dahlia for 7 block. I raced,
because Ritual compounds and blocking one 6 costs a whole card.

**Turn 4.** Damp Cultist at 13 with Strength 10. Deep Current+ (9) + Feint (6).
**No rejected alternative — this turn presented no decision.**

---

## Companions and offers

Every Companion card the run showed me, quoted as printed. All six arrived in
the fourth slot the Tamakushi Casket promises, or on the shop shelf.

1. **Sucrose — Catalyst Conversion (proto)** — cost 0, skill
   *Gain 1 Energy. Draw 1 card. Exhaust.*
   Makes sense as a card; makes no sense as a *Companion*. Nothing about it
   touches the Kurage, an aura, or a Plan — it is a colourless cantrip wearing
   a character's name. Passed.

2. **Sayu — Yoohoo Art: Fuuin Dash (proto)** — cost 1, attack
   *Deal 8 damage to a random enemy and Swirl it.*
   *Swirl — The enemy's aura is consumed and copied onto ALL enemies. No aura, no effect.*
   Reads clearly and sits right next to the kit: Deep Current sprays Hydro onto
   everything, so Swirl has something to spread. "Random enemy" is the part that
   made me pass — the kit's whole Plan layer is about deciding a turn early, and
   a random target is the opposite of that.

3. **Kujou Sara — Tengu Stormcall (proto)** [Electro] — cost 1, attack
   *Deal 5 damage. Next turn, your Attacks deal 5 additional damage.*
   *Applies Electro — If the target has no aura, this applies Electro for 2 turns. A different aura is consumed to trigger a Reaction instead.*
   Taken. The best-integrated card I was offered: it is the only Electro in a
   deck that paints Hydro on everything, so it is the only card that can make a
   Reaction happen, and "next turn" is the kit's native tense. In play it also
   gains the contextual `Reaction preview: Electro-Charged` line the moment a
   target has an aura, which is the single best piece of teaching on any screen
   I saw.

4. **Dahlia — Favonian Favor (proto)** — cost 1, skill
   *Gain 7 Block. Whenever an Elemental Reaction happens this turn, gain 3 Block.*
   Taken. Sensible next to the kit in principle. In practice its rider never
   once fired: I had exactly one Reaction all act, and it was on a turn I did not
   play Dahlia. With one Electro card in twenty, "whenever an Elemental Reaction
   happens this turn" is a dead line, and the card is a 7-block Defend.

5. **Gorou — Crystal Collapse** — cost 1, skill
   *Play on the Bake-Kurage. Plan: play a copy of the last other Companion card you played this turn.*
   Passed, and the reason is a defect: **I could not work out what "this turn"
   means.** The Plan resolves at the start of my *next* turn, so "the last other
   Companion card you played this turn" either means the turn I wrote the plan
   (in which case say "last turn", which is what the sibling card Chain of
   Command actually says) or the morning it fires (in which case it is almost
   always nothing, since the morning is before I have played anything). Two
   cards in the same kit describe the same window with opposite words.

6. **Rosaria — Ravaging Confession** [Cryo] — cost 1, attack
   *Deal 9 damage. If the enemy has an aura, apply 1 Vulnerable.*
   *Applies Cryo — If the target has no aura, this applies Cryo for 2 turns. A different aura is consumed to trigger a Reaction instead.*
   Taken. 9 damage for 1 is the biggest single-target number in the deck, the
   aura clause is live essentially always because Deep Current/Feint/Slack Water
   keep Hydro up, and the Vulnerable feeds the Casket for 2 more.

Also on the shop shelf, unbought and quoted for the record:
**Chiori — Fluttering Hasode** (cost 1, skill — *For 3 turns, at the end of your
turn deal 6 Geo damage to a random enemy, ignoring Block. Exhaust.*) — I bought
this one, 78 gold — and **Gorou — Juuga: Forward Unto Victory** (cost 1, skill —
*For 3 turns, at the end of your turn deal 6 Geo damage to a random enemy.
Exhaust.*), which is the same card without "ignoring Block" for 6 gold less.

Two Companion payoff cards were offered that I never had the density to take:
**The General's Banner** (*Once per turn, when you play a Companion card, apply 1
Weak to the front enemy*) and **Chain of Command** (*Play on the Bake-Kurage.
Plan: Deal 6 damage for each Companion card you played last turn*). With 4
Companions in 20 cards, Chain of Command is a 6-damage card most mornings, and
it is priced and worded as though it were the payoff of a built archetype.

---

## The kit, after 6 fights

**(a) What felt like a real choice, and what it traded off.**

- **Bank it or spend it.** Every Plan card is two cards: a thing now, or a
  bigger thing one turn later, paid now. Kurage's Oath 7-AoE-tomorrow versus
  three Strikes today is a genuine tempo-for-value trade and it came up in every
  fight. The Kurage taking *two* plans, in a printed order, makes it a real
  budget rather than a toggle.
- **Whether the Plan line beats the card's own face.** Slack Water and Feint
  both have faces and Plans, and which is better flips on the board: Slack
  Water's face beats its Plan against one enemy (damage plus a Weak *in time to
  matter*), and its Plan beats its face against three. Feint's Plan is 10 vs 6
  — until Fantastic Voyage makes the face 11 and the card prints both numbers so
  you can see the flip. That is the kit at its best.
- **Killing into Ravenous.** Killing one Corpse Slug stuns every other one and
  hands them +4 Strength. Free turn now, worse enemies later. Legible, and it
  changed my play twice.
- **The elite's cap.** Reading `Hardened Shell 0` and *stopping attacking* —
  playing a Plan and a debuff instead of two attacks that would have done
  nothing — is the most interesting turn I played, and the Plan layer is what
  made a good answer exist.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** Eight of my twenty cards, and I never once thought
  about either. Every "no decision" turn in this record is a turn where the hand
  was Strikes.
- **Slack Water's Plan line** (Weak to all, no damage) and **Stolen Chapter's
  Plan line** (draw 4) were both, on inspection, worse than the card's face in
  nearly every board I actually had — because the deck is 20 one-cost cards and
  3 energy, so extra cards are dead and a Weak that arrives tomorrow arrives
  after the hit it was meant to soften.
- **Song of Pearls** installed for 1 energy and paid 3 Block on exactly one turn
  before the fight ended. In a fight lasting 4 rounds it is roughly a Defend
  that cost me a turn of tempo.
- **Dahlia's Reaction rider** never fired. See above.

**(c) What I could not understand, or that contradicts its own printed text.**

1. **`Kokomi Burst: 5/20 … no rule for how it is spent`.** A meter appeared on
   my status line in round 4 of two separate fights, climbed to 15/20, and I
   finished the act without any card, relic or keyword box ever mentioning it.
   I could not spend it, could not tell what filled it, and could not tell
   whether I was playing badly by ignoring it. It is the only thing on any
   screen that named the character.
2. **`Hardened Shell 6 (buff) — Skulking Colony cannot lose more than 20 HP each
   turn.`** The number on the line and the sentence on the line disagree. The
   number is the remaining allowance; the sentence is the maximum. Nothing says
   so.
3. **Rider names do not match their cards.** Chiori — Fluttering Hasode leaves a
   buff called **Tamoto**. Kujou Sara — Tengu Stormcall leaves a buff called
   **Fantastic Voyage**. Neither name appears on the card that made it, so the
   status line cannot be traced back to what you played.
4. **Electro-Charged is described twice, differently.** The card's preview says
   "a 4-damage decaying damage-over-time effect"; the board says
   `Poison 4 (debuff)`.
5. **The morning log under-reports.** `Bake-Kurage: War Council, 5` prints the
   Plan's damage and silently omits the Tamakushi Casket's 2-per-enemy that fires
   off the same card's Weak, so the board moves by 7 and the line says 5. Every
   morning of the run needed arithmetic to reconcile.
6. **Gorou — Crystal Collapse's "this turn"** on a card that resolves next turn,
   when its sibling Chain of Command says "last turn" for what looks like the
   same window.
7. **A rule I only found by testing:** the Bake-Kurage's morning damage counts
   against the *same* turn's HP-loss cap as your hand. Banked damage is not free
   damage against a capped enemy, and nothing on the Plan keyword hints at it.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- Never wanted: **Defend.** Five block, three under Frail, in a kit whose whole
  proposition is deciding a turn early — the most reactive possible card, and
  there are four.
- Happiest to draw: **Slack Water (proto).** It is quietly the best card in the
  starter deck because the Casket turns its Weak into damage, so it is a Strike
  that also shrinks the next hit; and it is the one starter card whose face and
  Plan line genuinely compete.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** Turn 1 of fight 1 offered three Plan cards, two
Defends and an AoE with three energy, against two enemies at full HP where
nothing on the board could be killed that turn. Spend now or write the morning
was a live question before I understood the kit, and the answer (write two,
spend one) was the right one for a reason I could state. The one thing the turn
did *not* tell me was that the Kurage would take a second Plan — I had to try it
to find out, and the page only says so after you have done it.

---

## Non-blindness declaration

- Commands used: only `GITS_LANE=1 python -m understudy.blindplay observe` and
  `GITS_LANE=1 python -m understudy.blindplay act "<command>"`. No other
  understudy subcommand was run — no `harness state`, no `scenario`, no
  `staged_turn`, no `soak`.
- Tools used: **Bash**, for every one of the above calls, and for two pieces of
  scratch: `mkdir -p` to create
  `review/qa/kokomi-round-4c-2026-09-02/`, and `sed -n '<range>p'` piped off
  `observe` on about a dozen calls to print only the section of the screen I
  needed. Twice my own overlapping `sed` ranges printed a section twice in my
  terminal; that doubling is my scratch, not anything the bridge printed.
  **Write**, once, for this file.
- I did not keep a separate notes file; the notes are this record.
- One `act` was refused: `play "Strike (1)" on "Corpse Slug"` in fight 4,
  answered with `nothing here is called 'Strike (1)'. What is on the screen:
  Defend (1), Defend (2), Kujou Sara — Tengu Stormcall (proto), Kurage's Oath
  (proto), War Council`. My mistake; the refusal was correct and its listing of
  the hand was enough to recover in one call.
- Twice, an `act` issued in the same shell line immediately after a `go` into a
  rest site returned `ok` but the screen had not changed (`rest` then `proceed`,
  and later `upgrade`). Re-issuing the command on its own worked both times. I
  am counting those two as accepted acts in my tally, since the bridge said ok.
- **Repo files read: none.**
