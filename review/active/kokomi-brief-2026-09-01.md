Status: OPEN (picks ruled 2026-09-01; slice one in progress)

# Kokomi — character brief, draft 2

**Written 2026-09-01. Paper only.** Same format as the Klee brief
(`klee-brief-2026-09-01.md`), same seven tests, written to be read in
fifteen minutes and argued with. Facts about the shipped kit come from a
cited census (`docs/kokomi-cards.yaml`, the Kokomi identity record, the
two playtest notes); facts about the source character from Game8 and
GameWith; the healing bounds are calibrated against Downfall's Slime Boss
(§15).

Draft 1 let her heal the enemy's chip back every turn. Your note: that
collapses the elite-or-skip question, and Ward was a second defence
mechanic that added nothing. **Draft 2 keeps "never above where you
started," bounds every heal to a chip, makes her HP the bar she spends to
set up, and uses plain Block.** §15 lists what moved.

---

## 0. The test this brief has to pass

The Klee brief's seven: three boards (§10), one contested thing (§5),
fight one (§8, script A), borrowed systems (§4, §6.5), the rule each Rare
breaks (§6), what the relic pays for (§8), and lore (§3).

## 1. The promise

You are the Divine Priestess of Watatsumi, and you do not fight. You plan,
you pray, and it wears you out. Your jellyfish carries the sea's weight
for you: every ritual you pay for in your own vitality builds the Tide,
and the Tide is either the wave you send at them now or the rest that puts
a little of you back. **Your body is the budget. Spend it to set up, hold
to recover a little, surge when the plan is ready.**

In play: Kokomi has the biggest HP bar in the roster and the worst
shield. Her setup cards cost her HP, out of Block first, so Block is fuel
as much as defence. The jellyfish pays a chip back on every turn she
holds, never enough to undo a real hit, and only up to where she walked
in. She wins by having spent exactly as much of herself as the plan
needed and no more.

**The obvious plan, from the starter:** feed the jellyfish, hold while it
pays you back, surge when it kills.

## 2. What the shipped kit is, and why it is one-dimensional

One paragraph, cited. Shipped: Exhaust gives Charge, Charge is never
spent, the jellyfish pulses for 4 plus 3 per Charge at the end of every
turn (`tier0/constants.py:560` to 648; identity record, Charge). Muster
turns a card into a random Inazuma companion. Your verdict on 2026-08-26:
Charge is "ridiculously powerful (often hitting for 100+)" and everything
else is "low numbers"; the best turn is "spam companion cards to block
until you can hit with the Charge"; Muster is "hope you get some block."
The richness brief: "Charge has no door," "the Exhaust choice usually
collapses to a coin flip," and only one of her twelve starting cards can
Exhaust, so a cold start never meets the kit. Underneath: the no-healing
law removed the thing she is, and the kit was rebuilt from Silent verbs
around a bank with no spend.

## 3. The lore audit

| Source | Fact | What it becomes |
|---|---|---|
| Kurage's Oath (Skill) | The Bake-Kurage sits on the field, hits on an interval, heals on an interval | The jellyfish is always out. It holds **Tide**; it **Surges** when told; it **Mends** a chip on the turns she holds (rules 1 to 4) |
| Her "energy" | She tracks her own energy: duties drain it, doing what she likes refills it | **Exert**: her rituals cost HP, Block first (rule 5). Holding refills a chip (rule 4) |
| Highest base HP in the source game; everything scales off Max HP | Her vitality is her stat | The biggest HP bar in the roster, and the budget she spends (§5) |
| Nereid's Ascension (Burst) | The Ceremonial Garment: her attacks heal while she wears it | **Garment**: a short window where her Attacks Mend a chip per hit (rule 6) |
| Sango Isshin (C6) | A heal on someone at 80%+ HP becomes Hydro damage | The Priestess Rare: Mend past her entry HP becomes the jellyfish's hit |
| Tamanooya's Casket (passive) | Casting the Burst keeps the jellyfish out | The relic: the jellyfish never leaves, and its chip heal has a per-fight cap |
| Crit Rate −100%, "Flawless Strategy" | She cannot crit; her numbers are planned, not lucky | She cannot gain Strength; Strength becomes Tide (rule 7) |
| Strategist of the Resistance, raised on treatises | She wins the fight before it starts | **Plan**: an effect that arrives at the start of her next turn, cheaper for the wait (rule 8) |
| Gorou, her general | He executes what she writes | Gorou's Personal repeats her orders (§7) |
| The Clouds Like Waves Rippling (C2) | Heals more on those under half HP | An Uncommon: the jellyfish's chip doubles while she is under half |
| Water's Edge (C1) | Her basic attack ends with a fish | Water's Edge is the basic Attack |

Not used: water-walking, Orobashi (a boss-Rare name at most), C4 attack
speed.

## 4. The rules of the kit

Eight sentences. If a rule is not here, it is a card.

1. **The Bake-Kurage** is on the field for the whole combat. It holds
   **Tide**, a number that starts at 0 and does not reset on its own.
2. **Tide** is added by her cards ("Tide +N").
3. **Surge**: a card that says it makes the jellyfish deal Hydro damage
   equal to the Tide to the target, then the Tide is 0.
4. **The pulse**: at the end of a turn in which she did not Surge, the
   jellyfish **Mends** her 2, never above the HP she entered the combat
   with, and never more than 8 in one combat. (The relic carries both
   numbers.)
5. **Exert N**: a cost printed on some of her Skills and Powers, never on
   an Attack. She loses N HP, taken from Block first.
6. **Garment**: a state for a stated number of turns. While she wears it,
   each of her Attacks that hits Mends her 2.
7. **Flawless Strategy**: she cannot gain Strength; Strength she would gain
   becomes Tide.
8. **Plan**: an effect that happens at the start of her next turn instead
   of now.

**Mend** is one word with one rule: heal, never above entry HP. Cards that
Mend outside the pulse exist only from Uncommon up and all Exhaust, so no
card heals twice. There is no other healing anywhere in her pool. The one
thing that fires by itself is the pulse, and that is what a jellyfish is.

Persistent UI: the Tide number on the jellyfish, the pulse's remaining
budget on the relic, the Garment turn count, and the pending Plans.

**What leaves:** the Charge bank, Exhaust as the engine and its rotation
voice law, Muster as a transform, the Discard/Sly economy, the deck-size
law, the verb-partition law, the Burst gate on the Garment, and the
no-healing law, which the Mend rule replaces. **What changes:** "no
self-damage" becomes "Exert on Skills and Powers only." She wears herself
out planning and praying, never punching. **What stays:** Hydro on every
Attack, Flawless Strategy.

## 5. The contested thing

**Her HP is a budget three things draw on.** The enemy's hits, her own
Exerts, and the plan's clock all take from the same bar, and only the
pulse and the Garment put anything back, in chips.

- **Exert now** buys Tide today, out of Block first. So a Block card is
  worth two things and she picks which: it stops the raider's 7, or it
  pays for Kurage's Oath without touching her HP. It cannot do both.
- **Hold** keeps the Tide growing and the pulse paying 2 back. On a turn
  she holds, one Exert 2 is free. On a turn she Surges, it is not.
- **Surge** ends the fight sooner, which is the only way to stop the chip,
  and gives up the turn's pulse to do it.

The cost is real in both directions because the healing is small on
purpose: a 30-point turn is a problem the pulse cannot solve, and eight
turns of holding cannot undo an elite. She leaves fights hurt, like
everyone, and more hurt than most when she over-Exerted. The question she
answers every turn is the strategist's: how much of me does this plan
need, and when does it pay?

**Calibration.** Downfall's Slime Boss (65 HP, Tackle: "Deal 13. Take 3
damage," Heart of Goo: heal 2 per Consume up to 8 per combat, true heals
at Uncommon with Exhaust, weak Block, a setup-heavy deck that expects to
take damage) is the same shape and it holds up over a full run. The pulse
is Heart of Goo's 2-up-to-8; Exert is Tackle's 3, moved off Attacks and
onto rituals; the Uncommon Exhaust heals are the same tier. Her HP bar is
bigger than his because her lore says so and because her Exerts are on
setup cards she plays every turn.

## 6. The three loops

### 6.1 Priestess — "feed, hold, surge" (the starter's plan)

- **A turn looks like:** Block, Kurage's Oath (Exert 2 out of the Block,
  Tide +5), an Attack, end turn; the jellyfish pays 2 back. Two turns of
  that, then the Surge card comes up and the Tide is 15 and a raider dies.
- **You draft:** Tidal Prayer (Exert 1, Tide +4, draw 1), High Tide (Exert
  3, Tide +10), Undertow (Surge, then Block equal to half the damage
  dealt), Song of Pearls (Power: the pulse Mends 3 and the budget is 12),
  The Clouds Like Waves (Power: under half HP the pulse doubles),
  Nereid's Ascension (Uncommon, Exhaust: wear the Garment for 2 turns),
  Cleansing Tide (Uncommon, Exhaust: Mend 6).
- **The payoff moment:** a 24-Tide Surge into the boss on the turn the
  Garment is on and three Attacks each put 2 back.
- **The decision every turn:** hold or surge. Holding is free setup and a
  chip; surging is damage now and no chip. The enemy's clock sets the
  exchange rate.
- **The Rare that breaks a rule:** *Sango Isshin* (Power): Mend that would
  go past her entry HP becomes Hydro damage to a random enemy. "Never
  above where you started" is gone, and a full bar is a weapon.
- **Weakness:** a big single hit, which the pulse cannot answer, and any
  fight where she cannot afford to hold.

### 6.2 Strategist — "the plan was written last turn"

- **A turn looks like:** two Plans and a Block, end turn, take the hit;
  next turn opens with a free 10, two energy and a Block already resolved
  before the hand is played.
- **You draft:** Battle Plan (Plan: 2 energy), Ambush (Plan: 10 to a
  random enemy), Read the Field (Block 3 now, Plan: Block 4),
  Contingency (Uncommon, Exhaust, Plan: Mend 6), Feint (4 now, Plan: 8),
  Treatise (Power: each Plan that resolves draws 1), War Council (Exert
  2, Plan: play the top two cards of the draw pile free).
- **The payoff moment:** the cultists' ramp lands on the turn her Plans
  do, and she priced it a turn ago.
- **The decision every turn:** now or next turn. Every Plan is cheaper
  than its now-version by the turn she waits, and the intent on the enemy
  is the information she buys it with.
- **The Rare that breaks a rule:** *The Art of War* (Power): a Plan also
  happens now. Rule 8's delay is gone.
- **Weakness:** intent changes, and fights that end before the Plans fire.

### 6.3 Commander — "Gorou, go"

The smallest loop until the companion layer is fixed (§7). Her cards make
each companion play feed the jellyfish.

- **You draft:** Rally (draw a Companion from the draw pile, Tide +2),
  Orders (Power: a Companion play is Tide +2), Vanguard (Exert 1: the
  next Companion this turn costs 0), Gorou's Personal, the Inazuma pool
  at its home weighting.
- **The Rare that breaks a rule:** *The General's Banner* (Power): the
  first Companion each turn is played twice.
- **Weakness:** she cannot draft the army herself. Priestess and
  Strategist must each win without a single companion.

### 6.4 Bridges

- Undertow: a Surge that Blocks. The Priestess's exit and the Strategist's
  favourite Surge.
- Contingency: a Mend she can schedule for the turn after the spike.
- Orders: companions become Tide.
- The Garment: any Attack-heavy draft reaches the chip heal.

### 6.5 Currencies, and which way they cross

- **HP → Tide** (Exert), **→ Plans** (War Council), **→ tempo** (Vanguard).
- **Block → Tide**, by paying an Exert with it instead of with HP.
- **Tide → damage** (Surge), **→ Block** (Undertow), **→ cards** (Reading
  the Tide, Uncommon: draw 1 per 5 Tide).
- **Holding → HP** (the pulse), **damage dealt → HP** (the Garment), both
  in chips.
- **Plans → energy, cards, damage, Mend, Block**, all a turn late.
- **Companions → Tide** (Orders).
- **Strength → Tide** (rule 7), which is how any shared Strength source
  in the mod reaches her without a card.

## 7. The companion layer, for her

One loop of three, never the starter's plan. Under the structure ruled
for Klee on 2026-09-01: Personals slot-sharing and one each, Gorou first
("Plan: play a copy of the last Companion you played this turn"); Inazuma
is her home nation, so the home weighting already shows her Sayu,
Shinobu, Thoma, Sara, Itto and Raiden. Stand-ins with their own names in
place of Inazuma Universals come from the per-character workshop: Thoma's
barrier as Block that pays an Exert, Shinobu's ring as a chip Mend on
Exhaust, Sara's stormcall as a Plan. Nothing here is authored. She has no
tag; her readers, if any, read "Companion."

## 8. The intended weakness, and how she survives anyway

**Her Block is the worst in the roster and she spends it on herself.**
Coral Guard is 5 for 1 and there are few Block cards in her pool; every
Exert eats Block before HP; the pulse is 2 a turn and stops at 8. Against
a fight of chip she outlasts anyone. Against a fight that hits for 20 in
one turn she is the character with the least between her and the hit.

| Defence | Trigger | Lore | Which loop |
|---|---|---|---|
| **Block** | Standard, scarce, contested by Exert | She is not a fighter | All |
| **The pulse** | End of a turn she held: Mend 2, up to 8 per fight | The jellyfish's interval | Priestess |
| **Undertow** (Uncommon) | Surge, then Block half the damage | The wave that recedes | Bridge |
| **Contingency** (Uncommon, Exhaust) | Plan: Mend 6 next turn | The fallback in the plan | Strategist |
| **Cleansing Tide** (Uncommon, Exhaust) | Mend 6 now | Her own prayer | Priestess |
| **The Clouds Like Waves** (Uncommon Power) | Under half HP the pulse is 4 | C2 | Comeback |
| **The Garment** (Uncommon, Exhaust) | Two turns of Attacks that Mend 2 | Nereid's Ascension | Priestess |

**Where the player feels it.** On the draft screen: Block cards are rare
in her pool and every good setup card says Exert. On the map: she leaves
fights hurt like everyone, more so when she over-Exerted, and elites cost
her HP exactly as they cost Ironclad. Rest sites are hers because her
entry HP is the cap on every Mend for the fight after. She feels the
missing Block the way Ironclad feels the missing draw. The healing is
load-bearing only in the sense that it makes holding a real choice, and
it is small enough that nothing about the run's HP economy changes.

## 9. What fight one teaches

Starter deck, ten cards: Water's Edge ×3 (1 energy: 6 damage), Coral
Guard ×3 (1 energy: Block 5), Kurage's Oath ×2 (1 energy: Exert 2, Tide
+5), Rising Tide (1 energy: 4 damage, Surge), Stolen Chapter (1 energy:
draw 1, Plan: draw 1).

Relic, **Tamanooya's Casket**: the jellyfish is on the field from the
start of every combat, and at the end of each turn she did not Surge it
Mends her 2, up to 8 per combat. It pays for the hold verb: without it,
holding is only waiting, and Exert is only a tax. With it, a held turn
pays the Exert back, which is the first thing the player learns.

Turn one, fight one, the player sees: Attacks, Block, a card that costs
HP and feeds the jellyfish, one card that cashes it, one Plan. At the end
of the turn, if she held, the jellyfish gives back the 2 she spent. Feed,
hold, surge is on the table with nothing hidden.

## 10. Failure modes, named

- **Unbounded healing.** Prevented three ways: the pulse is 2 and stops
  at 8; card Mends are Uncommon-and-up and Exhaust; nothing Mends above
  entry HP. Sango Isshin, the one Rare that touches the cap, converts the
  excess to damage and heals nothing extra.
- **Free setup.** If Exert is too cheap or the pulse too big, Tide is free
  and the bank comes back. Exert must be at least as big as the pulse,
  and the pulse must stop before the fight does.
- **The doom clock.** Tide that grows every turn and pays once. Tide grows
  only by her cards, each of which costs HP; the enemy's clock makes
  holding expensive; Surge cards exist at Common.
- **Block as fuel only.** If Exert-from-Block is efficient enough, she
  never takes a hit to it. Prevented by few Block cards at ordinary rates
  and Exerts that exceed a single Block card.
- **Companion-locked.** Two loops win without a companion.
- **Plans that never fire.** The Strategist's weakness, kept.
- **Word salad.** Six keywords: Tide, Surge, Exert, Mend, Plan, Garment.
  Pick 7.

## 11. The three-board test (turn five)

**Board A, Priestess.** Act-1 boss at 95, Crush 20 next turn. Kokomi 58
of 80, Tide 14, pulse budget 4 left. Hand: Rising Tide, Coral Guard ×2,
Kurage's Oath, Undertow. Right play: Undertow (Surge 14, Block 7), Coral
Guard twice (Block 17), Kurage's Oath (Exert 2 from Block, Tide 5). Take
3. No pulse. The alternative, holding for a 19 next turn, eats 20 minus
10 through two Guards and gets 2 back. **Verb: surge, because the spike
is now.**

**Board B, Strategist.** Two Damp Cultists, both hitting 11 next turn, 16
after. Kokomi 60 of 80. Hand: Ambush, Battle Plan, Contingency, Water's
Edge, Coral Guard. Right play: Contingency (Plan: Mend 6), Ambush (Plan:
10), Coral Guard, hold. Take 17 to 43, pulse to 45. Next turn opens with
Mend 6, a free 10 and Battle Plan's energy before the 16s. **Verb: write
it down now.**

**Board C, Commander.** Three raiders, the Brute at 20 roaring. Kokomi 66
of 80, Orders in play. Hand: Rally, Vanguard, Thoma — Blazing Barrier,
Water's Edge, Rising Tide. Right play: Vanguard (Exert 1), Thoma for 0
(Block 5, Tide 2), Rally finds Shinobu (Tide 2), Shinobu's ring (3 to all,
Block 4, Tide 2). Tide from 9 to 15; Rising Tide on the Brute for 19.
**Verb: give orders, then cash them.**

Three boards, three verbs, and on each one the HP she has is the sum of
what she chose to spend.

## 12. Turn scripts

Kokomi 80 HP. Enemies from the dossiers.

### Script A — fight one, Ruby Raiders (the starter's plan)

**Enemies:** Axe Raider 21 (Swing 5 and 5 Block, Swing 5, Big Swing 12).
Crossbow Raider 19 (Reload 3 Block, Fire 14). Brute Raider 32 (Beat 7,
Roar +3 Strength).

**Turn 1.** Hand: Water's Edge ×2, Kurage's Oath, Coral Guard, Stolen
Chapter. Energy 3. Incoming: Axe 5, Crossbow 0, Brute 7.

Coral Guard (Block 5). Kurage's Oath: Exert 2 comes out of the Block,
leaving 3; Tide 5. Water's Edge into the Axe (21 to 15). Hold. The pulse
would Mend 2, but she is at 80, so nothing. Take 12 through 3: 71. The
first lesson is on the table: Exert ate the Block, and holding did
nothing because she was whole. Next turn it will.

**Turn 2.** Hand: Water's Edge, Coral Guard ×2, Kurage's Oath, Rising
Tide. Tide 5. Incoming: Axe 5, Crossbow 14, Brute 0 (Roar).

Two lines. Hold: Coral Guard twice (Block 10), Kurage's Oath (Exert 2
from Block, Tide 10). Pulse Mends 2: 73. Take 19 through 8: 62. Surge:
Rising Tide into the Axe at 15, 4 plus 5, to 6; Water's Edge kills it.
Coral Guard (Block 5). No pulse. Take 14 through 5: 62. Same HP either
way; the surge line has one raider fewer and Tide 0, the hold line has
Tide 10 and three raiders. She surges, because a dead Axe is 5 less every
turn from here, and that is the second lesson: cash when it kills.

**Turn 3.** Reshuffle. Hand: Water's Edge ×2, Kurage's Oath, Coral Guard,
Stolen Chapter. Tide 0. Incoming: Crossbow Reload, Brute Beat 10.

Kurage's Oath (Exert 2 from HP: 60, Tide 5). Water's Edge twice into the
Brute (32 to 20). Stolen Chapter (draw 1, Plan: draw 1). Hold: pulse Mends
2, 62. Take 10: 52. **What the script shows:** an Exert paid from HP and
given back by holding; the Brute is the clock, and the player is now
counting Tide against its HP.

**Turn 4.** Hand: Coral Guard ×2, Rising Tide, Kurage's Oath, Water's
Edge, plus the Plan's card. Tide 5. Incoming: Crossbow 14, Brute Roar.
Coral Guard twice (Block 10), Kurage's Oath (Exert 2 from Block, Tide 10),
Water's Edge into the Brute (20 to 14). Hold: Mend 2, 54. Take 14 through
8: 48. **Turn 5:** Rising Tide into the Brute, 4 plus 10, dead. Two
Attacks into the Crossbow. The fight ends on turn six with Kokomi near
45. It cost her more than it costs Ironclad, which is the Slime Boss
shape, and the pulse paid 6 of its 8. Four lessons: Exert eats Block
first; holding pays the Exert back; surge when it kills; you leave hurt.

### Script B — act-1 boss, single enemy (Priestess, hold or surge)

**Deck additions:** High Tide, Undertow, Song of Pearls, Nereid's
Ascension, Ambush, Tidal Prayer. **Boss (stand-in):** 140 HP, Swing 12,
Swing 12, Crush 20 and gains Block, repeat.

**Turn 1.** Hand: Song of Pearls, Kurage's Oath, Coral Guard, High Tide,
Water's Edge. Song of Pearls (1). Coral Guard (Block 5). High Tide (Exert
3 from Block, Tide 10). Hold: pulse 3 (she is at 80, nothing). Take 12
through 2: 70.

**Turn 3.** Tide 24 after two more feeds, pulse budget 6 left. Hand:
Undertow, Nereid's Ascension, Water's Edge ×2, Coral Guard. Kokomi 60 of
80. Incoming: Crush 20.

The decision the loop exists for. Surge: Undertow (24 to the boss, Block
12), Coral Guard (Block 17), Water's Edge twice (12 more). Take 3: 57.
Tide 0, no pulse. Hold: Nereid's Ascension (Garment 2 turns), Water's
Edge twice (12, Mend 4), Coral Guard. Pulse 3: 67. Take 15: 52. Tide 24
still on the jellyfish, growing, and the Garment on for next turn's
Attacks. Surge paid 36 damage and kept her at 57; hold paid 12 damage,
put 7 back, and kept the 24 for a turn when the boss is not gaining
Block. She holds, because the Crush turn is the boss's Block turn and a
Surge into Block is a Surge wasted. **What the script shows:** surge and
hold are both right on different turns, and the boss's own pattern says
which.

### Script C — two Damp Cultists (Strategist)

**Deck:** starter plus Battle Plan, Ambush ×2, Contingency, Read the
Field, Treatise. **Enemies:** two Damp Cultists, 52 HP each: Incantation
on turn one, then Dark Strike climbing 1, 6, 11, 16, 21.

**Turn 1.** Both chant. Hand: Ambush, Battle Plan, Treatise, Water's Edge,
Kurage's Oath. Treatise (1), Ambush (Plan: 10), Battle Plan (Plan: 2
energy). Hold; no damage in, nothing to Mend. **Turn 2** opens: Ambush
fires (10 into a cultist), Battle Plan pays 2, Treatise draws 2. Five
energy, seven cards, against a 1 and a 1. She Plans again: Ambush,
Contingency (Plan: Mend 6), Read the Field (Block 3, Plan: Block 4),
Kurage's Oath (Exert 2 from Block, Tide 5), two Attacks. **Turn 4** opens
with the second Ambush, a Mend 6 and a Block 4 before the 11s land, and a
Tide of 15 for the Surge card when it comes. The fight ends on turn five
before the 16s exist. **What the script shows:** the Strategist beats the
ramp by being a turn ahead of it, and Exert is what she paid to be there.

## 13. Defaults taken, and the things that are genuinely yours

**Ruled 2026-09-01: all eight at their defaults.** Your words are in the
commit. The list stands as it was put, so the ruling can be read against
it.

1. **How healing is bounded.** (1) *The pulse: 2 on a held turn, 8 per
   combat, on the relic; card Mends Uncommon and up, all Exhaust; nothing
   above entry HP* [default, the Slime Boss shape]. (2) No per-turn pulse;
   held Tide Mends at the end of combat instead, capped at 8. (3) No true
   healing at all; the pulse gives Block instead. The numbers 2 and 8 are
   the Balance stage's; the shape is the pick.
2. **Exert.** (1) *Her setup Skills and Powers cost HP, Block first; no
   Attack does* [default]. (2) Exert on Attacks too, Tackle-style. (3) No
   Exert; setup costs energy only, and the pulse is pure gain, which I
   would argue against.
3. **The starter's plan.** (1) *Priestess: feed, hold, surge* [default].
   (2) Strategist: two Plan cards in the starter, no Surge card.
4. **The Commander loop.** (1) *Stays, smallest of three, Gorou first*
   [default]. (2) Dropped. (3) Promoted, which is the shipped mistake.
5. **The Garment.** (1) *Uncommon, Exhaust, two turns of Attacks that
   Mend 2* [default]. (2) In the starter, replacing one Coral Guard.
   (3) Rare, four turns.
6. **Her HP.** (1) *Stays at 80 for the prototype; the direction is up,
   never down, and the number is Balance's* [default; a derived number].
   (2) Set it now, above Ironclad's, on the lore.
7. **Keyword budget.** (1) *Six: Tide, Surge, Exert, Mend, Plan, Garment*
   [default, under Klee pick 5's rule]. (2) Fold Garment into its one card:
   five.
8. **What leaves.** (1) *The Charge bank, the Exhaust engine and its
   voice law, Muster as transform, the Sly economy, the deck-size law, the
   verb partition, the Burst gate, the no-healing law; "no self-damage"
   becomes "Exert on Skills and Powers only"* [default]. (2) Keep Exhaust
   as a secondary verb: Exhaust is Tide +1. (3) Keep Muster as a Commander
   Uncommon.

Picks 6 and 7 are taken at their defaults unless you say otherwise. The
rest are design picks.

## 14. What this document does not do, and two things to watch

Two watch items from the ruling, carried into the slice-one gate and the
Balance stage:

- **How easy it is to stay fully healed across a run.** The measure is her
  HP at fight exit against Ironclad's on the same fights, by fight class
  (hallway, elite, boss), and how often a fight ends with the pulse budget
  unspent. If she leaves hallways at entry HP more often than he does, the
  pulse or Exert moves before anything else.
- **The Commander loop is only as good as the companion cards.** Its
  strength is measured after the companion workshop, not before, and a
  weak Commander read before then is not a Kokomi defect.


It does not author the sheet, price a card, or claim a winrate. It does
not decide any Watatsumi relic beyond the Casket. It does not author a
stand-in or Gorou's Personal. It does not settle whether "entry HP" means
the HP she walked in with or her Max HP; the default is walked in with,
because it makes rest sites hers. Nothing here is a ruling.

## 15. What your note changed (draft 1 → draft 2)

- **Ward is gone.** Plain Block, scarce. The "defence she plans" feel comes
  from Plan cards that grant Block next turn.
- **Healing is chips, bounded on the relic.** Draft 1 Mended for the whole
  Tide every turn, which let her heal back a fight's chip and removed the
  elite-or-skip question. Now the pulse is 2 a turn, 8 a fight, only on
  held turns; card Mends are Uncommon-and-up and Exhaust; the entry-HP cap
  stays. Your test, "take 30 in a turn but heal 5 a turn and you still
  have a problem," holds by construction.
- **Exert is new.** Your "HP is her energy bar, hitting Block first,"
  the Slime Boss's Tackle moved onto her rituals. It is what the pulse
  pays back, so the healing pays for her own spending before it touches
  the enemy's.
- **Surge is the cash verb.** Your "hold or spend the Tide." Tide no
  longer resets on its own; a card spends it, and holding earns the chip.
- **Overflow is now a Rare, not a rule.** Sango Isshin.
- **Calibration named.** Downfall's Slime Boss: 65 HP, Heart of Goo (2
  per Consume, 8 per combat), Tackle ("Deal 13. Take 3 damage," Block
  absorbs it), Corrosive Spit (0 cost, 6 damage, heals 2), true heals at
  Uncommon with Exhaust, weak Block, setup-heavy. Sources: the Downfall
  wiki (wiki.gg mirror; the fandom page returns 402) and a Japanese
  player guide for the Block-absorbs-Tackle detail.
