Status: OPEN (picks 1 to 8)

# Kokomi — character brief, draft 1

**Written 2026-09-01. Paper only.** Same format as the Klee brief
(`klee-brief-2026-09-01.md`), same seven tests, written to be read in
fifteen minutes and argued with. Facts about the shipped kit come from a
cited census (`docs/kokomi-cards.yaml`, LAW.md lines 225 to 272, the two
playtest notes); facts about the source character from Game8 and GameWith.

---

## 0. The test this brief has to pass

The Klee brief's seven: three boards (§10), one contested thing (§4), fight
one (§8, script A), borrowed systems (§3, §5.5), the rule each Rare breaks
(§5), what the relic pays for (§8), and lore (§2).

## 1. The promise

You are the Divine Priestess of Watatsumi, and you do not fight. You plan.
Your jellyfish heals what the enemy took from you, and hits them with
whatever you did not need healed. **The healthier you are, the harder the
sea hits.** The only questions are how much damage you are willing to take,
when the heal arrives, and whether the plan you wrote last turn still holds.

In play: Kokomi is the one character who heals in combat, and the price is
that she cannot block on demand. Her defence arrives after the hit, not
before it, so every enemy turn is a bet she has already placed. When she is
right, she ends the turn at full health and the jellyfish's pulse becomes a
wave. When she is wrong, the heal goes to keeping her alive and the wave
never comes.

**The obvious plan, from the starter:** feed the jellyfish, stay healthy,
let it hit. Everything else branches from that.

## 2. What the shipped kit is, and why it is one-dimensional

One paragraph of diagnosis, cited, then the rest of the brief is design.

Shipped: Exhaust gives Charge, Charge is never spent, the jellyfish pulses
for 4 plus 3 per Charge at the end of every turn (`tier0/constants.py:560`
to 648, LAW 247 to 250). Muster turns a card into a random Inazuma
companion. The playtest verdict, your words on 2026-08-26: Charge is
"ridiculously powerful (often hitting for 100+)" and everything else is
"low numbers"; the best turn is "spam companion cards to block until you
can hit with the Charge"; Muster is "hope you get some block." The richness
brief agrees: "Charge has no door," "the Exhaust choice usually collapses
to a coin flip," and only one of her twelve starting cards can Exhaust at
all, so a cold start never meets the kit. Underneath: the no-healing law
(LAW 229 to 231) removed the thing she is, and the kit was rebuilt out of
Silent verbs and a bank with no spend.

## 3. The lore audit

| Source | Fact | What it becomes |
|---|---|---|
| Kurage's Oath (Skill) | The Bake-Kurage sits on the field and, on an interval, heals the party and hits nearby enemies | The jellyfish is always out; it pulses at the end of her turn: **Mend** first, **Overflow** with the rest (rules 1 to 3) |
| Nereid's Ascension (Burst) | The Ceremonial Garment: her attacks heal the party while she wears it, scaled by Max HP | **Garment**: a state where her Attacks Mend for the damage they deal (rule 5) |
| Sango Isshin (C6) | A heal that lands on someone already at 80%+ HP becomes Hydro damage | **Overflow**: Mend beyond her starting HP becomes the jellyfish's hit (rule 3), and the Rare that spreads it |
| Song of Pearls (passive) | Healing Bonus feeds her damage bonus | Uncommon Power: Overflow deals more |
| Tamanooya's Casket (passive) | Casting the Burst refreshes the jellyfish | The relic: the jellyfish never leaves the field |
| Crit Rate −100%, "Flawless Strategy" | She cannot crit. Her numbers are steady and planned | She cannot gain Strength; Strength becomes Tide (rule 7). No spike mechanics anywhere in her pool |
| Strategist of the Resistance, raised on military treatises | She wins before the fight by planning it | **Plan**: a card whose effect arrives at the start of her next turn, cheaper than doing it now (rule 6) |
| Gorou, her general | He executes what she plans | Gorou's Personal repeats her orders (§7) |
| Introverted, tracks her own "energy," hates the ceremonial duties | Her resources drain doing what she must and refill doing what she likes | The map weakness (§6): she cannot end a fight above the HP she brought in, so rest matters more to her than to anyone |
| The Clouds Like Waves Rippling (C2) | Heals more on party members under half HP | An Uncommon: Mend doubles while she is under half |
| Water's Edge (C1), fish on the last hit | Her basic attack ends with a jellyfish jab | Water's Edge is the basic Attack; the "fish" is a Common that both hits and feeds Tide |
| Max HP scales everything | Her power is her vitality | Mend is capped at the HP she entered with; the cap is the resource |

Not used: water-walking (cosmetic), the serpent god Orobashi (a boss-fight
Rare name at most), C4 attack speed.

## 4. The rules of the kit

Seven sentences. If a rule is not here, it is a card.

1. **The Bake-Kurage** is on the field for the whole combat. It holds
   **Tide**, a number that starts at 0.
2. **Tide** is added by her cards ("Tide +N"). At the end of her turn the
   jellyfish **pulses**: it Mends her for the Tide, then the Tide is 0.
3. **Mend N** heals N, never above the HP she started this combat with. Any
   Mend that would go past that cap is **Overflow**: the jellyfish deals
   that much Hydro damage to a random enemy instead.
4. **Ward N** is a shield that does not expire at the end of the turn. It is
   her only way to stop damage before it lands. Her pool has no Block.
5. **Garment** is a state that lasts a stated number of turns. While she
   wears it, her Attacks Mend her for the damage they deal.
6. **Plan** is a card effect that happens at the start of her next turn
   instead of now.
7. **Flawless Strategy**: she cannot gain Strength; Strength she would gain
   becomes Tide. Her numbers do not spike, they arrive.

The one thing that fires by itself is the jellyfish's pulse, and that is
what a jellyfish is. Persistent UI: the Tide number on the jellyfish, her
Ward, the Garment turn count, and the pending Plans. That is the whole
rules display.

**What leaves:** the Charge bank, Exhaust as the engine and the rotation
voice law, Muster as a transform, the Discard/Sly economy, the deck-size
law, the verb-partition law, the Burst gate on the Garment, and the
no-healing law, which rule 3 replaces. **What stays:** no self-damage (she
does not hurt herself; the enemy does that), Hydro on every Attack, and
Flawless Strategy.

## 5. The contested thing

**Her HP is the resource, and it is wanted two ways.** Damage taken is
what Mend is for; damage not taken is what Overflow is for. Every point of
Tide is either a heal or a hit, and which one is decided by how much she
has lost when the pulse arrives. So:

- Warding a hit costs a card that could have been Tide or an Attack, and
  pays in Overflow next pulse.
- Taking the hit costs nothing now, and pays in a pulse that only heals.
- Mending during her turn (the Garment, Cleansing Tide) moves the line
  before the pulse, which is how she turns a heal-turn into a hit-turn.

The cost either way is real because the enemy's next turn is a bet she
cannot hedge after the fact: her heal lands before the enemies act, so she
enters every enemy turn with whatever HP the last pulse left her. A single
enemy turn that exceeds her HP kills her, and no card in her pool stops it
after it starts. That is the whole weakness, and it is what makes staying
healthy a choice rather than a default.

**The honest version of the trade.** Tide +5 for one energy and Block 5 for
one energy are worth the same against chip damage. Tide is better when the
hit does not come (it becomes damage) and worse when the hit is lethal (it
never arrives). Her rates are set below Block's, and her Ward below Block's,
so that the difference is the decision and not free value.

## 6. The three loops

### 6.1 Priestess — "stay whole and the sea hits" (the starter's plan)

Feed Tide, keep HP at the cap, let every pulse Overflow.

- **A turn looks like:** Ward the intent that matters, one Attack, one Tide
  card, end turn; the jellyfish hits for what she did not lose.
- **You draft:** Sea Spray (Attack plus Tide), Tidal Prayer (Tide plus
  draw), Cleansing Tide (Mend now, so the pulse can Overflow), Song of
  Pearls (Overflow deals more), Slack Tide (hold the pulse: Tide carries a
  turn, the Cook of this kit), Nereid's Ascension (the Garment, for the
  turn she wants to attack and heal at once).
- **The payoff moment:** a 14-Tide pulse against a full bar, all of it a
  wave.
- **The decision every turn:** "do I spend a card to stay whole, or take
  it and let the pulse pay for it?" Slack Tide sharpens it: hold two pulses
  for one big one, and be hurt for a turn while you do.
- **The Rare that breaks a rule:** *Sango Isshin* (Power): Overflow hits
  every enemy. Rule 3's "a random enemy" is gone.
- **Weakness:** big single hits, which turn every pulse into a heal, and
  Strength ramps.

### 6.2 Strategist — "the plan was written last turn"

Plans: cheaper effects that arrive at the start of next turn. A quiet turn
of writing, then a turn where everything fires before she has drawn.

- **A turn looks like:** two Plans and a Ward, end turn, take the hit; next
  turn starts with a free 10, two energy and a Mend already resolved, and
  the hand is played on top of that.
- **You draft:** Battle Plan (Plan: energy), Ambush (Plan: damage),
  Contingency (Plan: Mend), Read the Field (Ward now and Ward later),
  Feint (small hit now, big hit next turn), Treatise (a Power: each Plan
  that resolves draws a card), War Council (Plan: play the top two cards of
  the draw pile free).
- **The payoff moment:** the enemy's Strength ramp arrives on the turn her
  Plans do, and she had it priced a turn ago.
- **The decision every turn:** now or next turn. A Plan is worth more than
  its now-version and costs a turn of not having it; the intent shown is
  the information she buys it with.
- **The Rare that breaks a rule:** *The Art of War* (Power): a Plan also
  happens now. Rule 6's delay is gone; she plays everything twice.
- **Weakness:** enemies that change intent, and any fight that ends before
  the Plans resolve, which wastes them.

### 6.3 Commander — "Gorou, go"

The Resistance. Companion cards are her army, and her own cards make each
order count. This loop leans on the companion layer and is the smallest of
the three until that layer is fixed (§7).

- **A turn looks like:** Rally finds a companion, Orders turns the play
  into Tide, Gorou repeats it.
- **You draft:** Rally (draw a Companion from the draw pile, Tide +2),
  Orders (Power: a Companion play is Tide +2), Vanguard (the next Companion
  costs 0 and Mends 3), Gorou's Personal, and the Inazuma pool at its home
  weighting.
- **The payoff moment:** a 0-cost Thoma barrier, repeated by Gorou, feeding
  4 Tide and 10 Ward on one energy.
- **The decision every turn:** which companion to spend the order on.
- **The Rare that breaks a rule:** *The General's Banner* (Power): the
  first Companion each turn is played twice. The one-play rule is gone for
  her army.
- **Weakness:** she cannot draft the army herself; it comes from the
  companion slot, and a run without companions makes this a worse
  Priestess deck. That is allowed. Priestess and Strategist must each win
  without a single companion.

### 6.4 Bridges

- Ebb (Uncommon Skill): Ward equal to your Tide; Tide becomes 0. Turns a
  heal-or-hit into a shield before the spike. Priestess's exit, Strategist's
  favourite.
- Contingency (Plan: Mend) moves the Mend to the start of next turn, which
  is before the enemy acts twice. The Strategist's answer to the lethal
  window.
- Orders makes companions Tide. Commander feeds Priestess.
- The Garment makes Attacks Mend, so any Attack-heavy draft reaches
  Overflow.

### 6.5 Currencies, and which way they cross

- **Tide → HP** (rule 2), **→ damage** (rule 3), **→ Ward** (Ebb), **→
  cards** (Reading the Tide, Uncommon: draw one per 5 Tide).
- **HP → tempo**: no Block means energy goes to Attacks and Plans, and the
  damage is paid back by the pulse.
- **Plans → energy, cards, damage, Mend, Ward**, all a turn late and all
  cheaper for it.
- **Companions → Tide** (Orders), **→ Mend** (Vanguard).
- **Damage dealt → HP** (the Garment), and so **→ Overflow**.
- **Strength → Tide** (rule 7), which is how any shared Strength source in
  the mod reaches her without a card.

## 7. The companion layer, for her

Kokomi's shipped kit revolved around companions because Muster made them
the engine. Here they are one loop of three and never the starter's plan.
Under the Klee brief's structure, ruled 2026-09-01:

- **Personals, slot-sharing, one each:** Gorou (her general, the executor:
  "Plan: play a copy of the last Companion you played this turn") and, if a
  second earns it, a Watatsumi Resistance card. Inazuma is her home nation,
  so the home weighting already shows her Sayu, Shinobu, Thoma, Sara, Itto
  and Raiden without Personal channel cost. Two Personals, inside R234 P5.
- **Stand-ins:** Kokomi-only cards with their own names in place of
  Inazuma Universals, by the same swap as Klee's. Candidates from the
  source kits: Shinobu's ring as a Ward that Mends, Thoma's barrier as Ward
  that carries Tide, Sara's stormcall as a Plan. The per-character workshop
  decides; nothing here is authored.
- **No tag.** She has no Hexerei equivalent; the Resistance is not a
  family in the game's sense. Readers, if any, read "Companion," which the
  engine already knows.

## 8. The intended weakness, and how she survives anyway

**She cannot stop a hit after it starts, and she cannot leave a fight
healthier than she entered it.** Her defence is a Ward she paid for a turn
ago or a Mend that arrives after the damage. Against a fight that hits for
chip she is the healthiest character in the mod; against a fight that hits
for 20 in one turn she is the most fragile.

| Defence | Trigger | Lore | Which loop |
|---|---|---|---|
| **The pulse** | End of her turn, Mend for the Tide | The jellyfish heals on its interval | All |
| **Ward** | Paid before the hit; stays until used | She plans the defence, she does not react | Strategist, Priestess |
| **Cleansing Tide** (Common) | Mend now, during her turn | The priestess's own prayer | Priestess |
| **Contingency** (Common, Plan) | Mend at the start of next turn | The plan had a fallback | Strategist |
| **The Clouds Like Waves** (Uncommon Power) | Under half HP, Mend is doubled | C2 | All, as a comeback |
| **Ebb** (Uncommon) | Convert Tide to Ward before a spike | The tide goes out | Bridge |

**Where the player feels it.** On the draft screen: there is no Block card
in her pool at all, and every Ward is 4 for 1. On the map: a fight ends on
her turn, so the last enemy turn's damage is never mended, and she walks
out of every fight down by one enemy turn. Elites that hit for 20 are a
real threat, rest sites are worth more to her than an upgrade, and a bad
entry HP is a cap she carries into the next fight. She feels the missing
Block the way Ironclad feels the missing draw. The weakness is load-bearing
because it is what makes "stay whole" a plan rather than a state.

## 9. What fight one teaches

Starter deck, ten cards: Water's Edge ×3 (1 energy: 6 damage), Kurage's
Oath ×2 (1 energy: Tide +5), Coral Ward ×3 (1 energy: Ward 4), Stolen
Chapter (1 energy: draw 1, Plan: draw 1), Nereid's Ascension (2 energy:
wear the Garment for 2 turns).

Relic, **Tamanooya's Casket**: the jellyfish is on the field from the start
of every combat. It pays for the whole Tide verb: without it every Tide
card is a blank, the way Sparks are blank without Pounding Surprise. The
player meets the relic's job at the end of turn one, when the first pulse
either heals or hits.

Turn one, fight one, the player sees: an Attack, a card that feeds the
jellyfish, a shield that does not go away, one Plan, and a two-cost card
that promises heals on hit. At the end of the turn the jellyfish does
something on its own, and the number it does it with is the one the player
fed it. The obvious plan is on the table: feed, stay whole, let it hit.

## 10. Failure modes, named

- **Delayed Block.** Tide that is only a heal with a delay. Prevented by
  Overflow, by Ebb, and by rates below Block's.
- **The doom clock.** A bank that grows every turn and pays once. Prevented
  by rule 2: the pulse spends the Tide. Slack Tide holds it for one turn at
  a cost; only the Rare *Tamanooya's Legacy* (Power: the pulse does not
  spend the Tide) brings the bank back, and it is a Rare because that is
  the shape you liked in the playtest, and it should be a choice and not
  the kit.
- **Free heal.** Healing that lifts the run's HP economy. Prevented by the
  cap: never above the HP she entered with, never past the last enemy
  turn.
- **The Ward wall.** If Ward is efficient enough, she never takes damage
  and Overflow is free. Prevented by pricing Ward under Block and giving
  her no Block at all; staying whole must cost cards.
- **Companion-locked.** Prevented as in Klee: two loops win without a
  companion.
- **Plans that never fire.** A fight that ends first wastes them; that is
  the loop's weakness and it stays. What is prevented is a Plan with no
  now-version to compare against; every Plan card should read as "cheaper,
  later" next to a Common the player knows.
- **Word salad.** Six keywords: Tide, Mend, Ward, Garment, Plan, Overflow.
  Pick 7.

## 11. The three-board test (turn five)

**Board A, Priestess.** Act-1 boss at 95, hits 14 next turn. Kokomi 78 of
80 (cap 80), Ward 0, Tide 0. Hand: Sea Spray, Kurage's Oath, Coral Ward
×2, Cleansing Tide. Right play: Coral Ward twice (Ward 8), Kurage's Oath
(Tide 5), Sea Spray (5 damage, Tide 2). Pulse: Mend 2 to the cap, Overflow
5. Take 6 through the Ward. She stayed near the cap and the jellyfish hit.
**Verb: stay whole.**

**Board B, Strategist.** Two Damp Cultists, the ramp arriving: both hit 11
next turn, 16 the turn after. Kokomi 60 of 80, Tide 0. Hand: Ambush,
Battle Plan, Contingency, Water's Edge, Coral Ward. Right play: Contingency
(Plan: Mend 8), Ambush (Plan: 10 to a random enemy), Coral Ward. Take 18
this turn to 42. Next turn opens with Mend 8 and a free 10, then Battle
Plan's energy and the hand on top, before the 16s land. **Verb: write it
down now, collect next turn.**

**Board C, Commander.** Three raiders, the Brute at 20 roaring. Kokomi 70
of 80. Hand: Rally, Vanguard, Thoma — Blazing Barrier, Water's Edge, Orders
already in play. Right play: Vanguard, then Thoma for 0 (Ward 5, Ward 2
next turn, Mend 3, Tide 2 from Orders), Rally finds Shinobu, Shinobu's
ring (3 to all, Ward 4, Tide 2). Tide 4 at the pulse against a bar at the
cap: Overflow 4. **Verb: give orders.**

Three boards, three verbs, and on each one the defence she has is the
verb she picked a turn ago.

## 12. Turn scripts

Kokomi 80 HP. Enemies from the dossiers.

### Script A — fight one, Ruby Raiders (the starter's plan)

**Enemies:** Axe Raider 21 (Swing 5 and 5 Block, Swing 5, Big Swing 12).
Crossbow Raider 19 (Reload 3 Block, Fire 14). Brute Raider 32 (Beat 7,
Roar +3 Strength).

**Turn 1.** Hand: Water's Edge ×2, Kurage's Oath, Coral Ward, Stolen
Chapter. Energy 3. Incoming: Axe 5, Crossbow 0, Brute 7.

Water's Edge twice into the Axe (21 to 9). Kurage's Oath: Tide 5. End of
turn, HP 80 of 80: nothing to Mend, so Overflow 5 hits a random raider,
say the Axe, to 4. Enemies: 12 in. Kokomi 68. The first lesson lands in
the first pulse: the jellyfish hit because she was whole.

**Turn 2.** Hand: Water's Edge, Coral Ward ×2, Kurage's Oath, Nereid's
Ascension. Incoming: Axe 5, Crossbow 14, Brute 0 (Roar).

Two lines. Quiet: Water's Edge kills the Axe, Kurage's Oath (Tide 5),
Coral Ward (Ward 4). Pulse Mends 5 to 73. Take 10 through the Ward: 63.
Loud: Nereid's Ascension (2) then Water's Edge (1) kills the Axe and Mends
6 to 74 under the Garment; no Tide, no pulse. Take 14: 60, Garment one
turn left. The loud line is behind by 3 HP and ahead by a Garment turn.
She takes it, because next turn's hand has Attacks in it.

**Turn 3.** Garment on. Hand: Water's Edge ×2, Stolen Chapter, Coral Ward,
Kurage's Oath. Incoming: Crossbow Reload, Brute Beat 10.

Water's Edge twice into the Brute (32 to 20), each Mending 6: 72. Kurage's
Oath: Tide 5. Pulse Mends 5 to 77. Take 10: 67. **What the script shows:**
the Garment turned Attacks into heals, the pulse followed, and she is
within 13 of the cap with the Crossbow's 14 due next turn. The player is
now reading intents for the first time, which is the character.

**Turn 4.** Hand: Coral Ward ×2, Nereid's Ascension, Kurage's Oath,
Stolen Chapter. Incoming: Crossbow 14, Brute Roar. Coral Ward twice (Ward
8), Kurage's Oath (Tide 5), pulse Mends 5 to 72. Take 6: 66. Turn five,
Brute Beat 13 due: Stolen Chapter's Plan draws, two Attacks kill the
Crossbow, the pulse Overflows. The fight ends on turn six with Kokomi near
60, and the last enemy turn's damage unmended. Four lessons: feed the
jellyfish; whole means it hits; the Garment is the loud turn; you walk
out down by one enemy turn.

### Script B — act-1 boss, single enemy (Priestess with Slack Tide)

**Deck additions:** Slack Tide, Sea Spray, Cleansing Tide, Song of Pearls,
Ebb, Ambush. **Boss (stand-in):** 140 HP, Swing 12, Swing 12, Crush 20 and
gains Block, repeat.

**Turn 1.** Hand: Song of Pearls, Sea Spray, Coral Ward, Kurage's Oath,
Slack Tide. Song of Pearls (1). Kurage's Oath (Tide 5). Sea Spray (5, Tide
2). End of turn at the cap: Overflow 7 plus 3 from Song of Pearls, 10.
Take 12: 68.

**Turn 3.** Slack Tide in play since turn two, Tide held at 9 from last
turn. Hand: Cleansing Tide, Kurage's Oath, Coral Ward, Ebb, Water's Edge.
Incoming: Crush 20. Kokomi 66 of 80.

The decision the loop exists for. Cash: Cleansing Tide (Mend 8, to 74),
Kurage's Oath (Tide 14), let it pulse: Mend 6 to the cap, Overflow 8 plus
3. Take 20 through nothing: 60. Hold: Ebb (Ward 9, Tide 0), Coral Ward
(Ward 13), Kurage's Oath (Tide 5), hold the pulse again. Take 7: 59. Next
turn the Tide is 5 held plus whatever she adds, against a 12, and she is
at 59. Cash paid 11 damage now; hold paid 6 Ward and a bigger pulse later.
She holds, because the Crush is the biggest hit the boss has and Ward is
worth most against it. **What the script shows:** Slack Tide makes the
pulse a choice; Ebb makes Tide a shield; both cost the hit she is not
healing.

### Script C — two Damp Cultists (Strategist)

**Deck:** starter plus Battle Plan, Ambush ×2, Contingency, Read the
Field, Treatise. **Enemies:** two Damp Cultists, 52 HP each: Incantation
turn one, then Dark Strike climbing 1, 6, 11, 16, 21 across turns two to
six.

**Turn 1.** Both chant. Hand: Ambush, Battle Plan, Treatise, Water's Edge,
Kurage's Oath. Treatise (1), Ambush (Plan: 10), Battle Plan (Plan: 2
energy). No damage in. **Turn 2** opens: Ambush fires (10 to a cultist),
Battle Plan pays 2, Treatise draws 2 for the two Plans. Five energy, seven
cards, against a 1 and a 1. She Plans again: Ambush, Contingency (Plan:
Mend 8), Read the Field (Ward 3 now, Ward 3 later), two Attacks. **Turn 4**
opens with the second Ambush and the Mend already done, the 11s arrive
against a Ward she bought two turns ago, and the fight is over on turn
five before the 16s exist. **What the script shows:** the Strategist beats
the ramp by being a turn ahead of it, and every Plan was cheaper than its
now-version by exactly the turn she waited.

## 13. Defaults taken, and the things that are genuinely yours

Numbered picks. Each has a default in italics.

1. **Healing comes back.** (1) *The no-healing law is replaced by rule 3:
   Mend never above the HP she entered with, Overflow past it* [default].
   (2) Keep the no-healing law; Tide becomes Ward instead of Mend and
   Overflow keys off unused Ward. (3) Healing uncapped, priced by rarity.
   This is the one pick that decides whether she is the priestess or
   another shield character.
2. **The pulse spends the Tide.** (1) *Yes; the bank you saw hit for 100
   returns only as the Rare Tamanooya's Legacy* [default]. (2) Tide
   persists and the pulse reads it, capped at some number.
3. **The starter's plan.** (1) *Priestess: feed, stay whole, let it hit*
   [default]. (2) Strategist: the starter carries two Plan cards and no
   Garment. (3) Both: Nereid's Ascension leaves the starter and a second
   Plan card enters.
4. **The Commander loop.** (1) *Stays, smallest of three, Gorou as the
   first Personal* [default]. (2) Dropped; Inazuma companions reach her
   only as Universals and stand-ins. (3) Promoted to the starter's plan,
   which is the shipped kit's mistake again.
5. **Ward does not expire.** (1) *Yes, priced under Block and with no Block
   in her pool at all* [default]. (2) Ward expires like Block and she keeps
   a Block basic. (3) Ward persists but caps at 15.
6. **Meter name.** (1) *Tide, replacing Charge* [default; a rename at
   Paper stage costs nothing]. (2) Keep Charge.
7. **Keyword budget.** (1) *Six: Tide, Mend, Ward, Garment, Plan, Overflow*
   [default, under Klee pick 5's rule]. (2) Fold Overflow into Mend's
   tooltip and Garment into the one card that grants it: four.
8. **What leaves.** (1) *The Charge bank, the Exhaust engine and its voice
   law, Muster as transform, the Sly economy, the deck-size law, the verb
   partition, the Burst gate, the no-healing law* [default]. (2) Keep
   Exhaust as a secondary verb with Tide +1 per Exhaust. (3) Keep Muster
   as a Commander Uncommon.

Picks 6 and 7 are process picks and are taken at their defaults unless you
say otherwise. The rest are design picks.

## 14. What this document does not do

It does not author the sheet, price a card, or claim a winrate. It does
not decide the Watatsumi relic beyond the Casket. It does not author a
stand-in or Gorou's Personal; those are the workshop's. It does not settle
whether "starting HP" means the HP she entered the fight with or her Max
HP; the default is entered with, because it makes rest sites hers, and the
Balance stage can move it. Nothing here is a ruling.
