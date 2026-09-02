Status: OPEN (draft 3 picks 1 to 7; the live Paper artefact through the Prototype build)

# Sangonomiya Kokomi: the brief, draft 3

Draft 3, 2026-09-02, after [USER]'s own prototype run sent draft 2 back to
the rules (`review/ruled/kokomi-overhaul-round-1-2026-09-02.md`, R237, and
the rework packet `review/ruled/kokomi-rework-2026-09-02.md`, R238, whose
direction A this is). §16 lists what moved. Everything a build needs is in
§4, §6 and §9; the rest is the reasoning.

## 0. The test this brief has to pass

The Klee brief's seven: three boards (§11), one contested thing (§5),
fight one (§9, script A), borrowed systems (§4, §6.5), the rule each Rare
breaks (§6), what the relic pays for (§9), and lore (§3).

## 1. The promise

You are the Divine Priestess of Watatsumi, and you do not fight. You give
orders, and the Bake-Kurage carries them out. Everything you let go of, it
remembers, and it does it again: the Block you raised, the prayer you
said, the companion you sent in. It acts once a turn, when the Tide can
pay for it, and when you tell it to Surge it does everything it remembers
at once. **Your deck is a set of orders. The jellyfish is the one who
executes them. Feed it, choose what it keeps, and pick the turn it sends
the whole wave.**

In play: Kokomi's cards come back. A card that Exhausts is not gone, it is
queued; a Plan is a card you pay for now and collect next turn; a
companion you Rally is a companion the jellyfish will play again. The Tide
is the fuel that keeps the queue moving, her Skills raise it, and Surge
spends all of it in one turn. She is a turn slow by nature and she wins by
having written the right things in the right order.

**The obvious plan, from the starter:** do a thing, the jellyfish does it
again, feed it so it can, Surge when the row is full.

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

Draft 2 replaced the bank with Tide, a number spent once by Surge, and
priced every step of it in HP (Exert) and turns (the pulse). Your run and
both seats did the same arithmetic and it lost to the basic attack; the
payoff was a ledger, not a moment. Draft 3 keeps the jellyfish and the
Tide and puts your Kurage's Memory back at the centre, with her own cards
in it.

## 3. The lore audit

| Source | Fact | What it becomes |
|---|---|---|
| Kurage's Oath (Skill) | The Bake-Kurage sits on the field, hits on an interval, heals on an interval | The jellyfish is always out. It **remembers** what she gives up and does it again, once a turn, when the **Tide** pays (rules 1 to 4); **Surge** is the wave (rule 5) |
| Her "energy" | She tracks her own energy: duties drain it, doing what she likes refills it | Retired in draft 3. Draft 2's Exert (rituals cost HP) read as a tax; her vitality is her HP bar, not a price |
| Highest base HP in the source game | Her vitality is her stat | The biggest HP bar in the roster, and the worst Block (§8) |
| Nereid's Ascension (Burst) | The Ceremonial Garment: her attacks heal while she wears it | **Garment**: a short window where her Attacks Mend a chip per hit (rule 7's Mend) |
| Sango Isshin (C6) | A heal on someone at 80%+ HP becomes Hydro damage | The Priestess Rare: Mend past her entry HP becomes the jellyfish's hit |
| Tamanooya's Casket (passive) | Casting the Burst keeps the jellyfish out | The relic: the jellyfish never leaves, and the first card it plays each fight costs no Tide |
| Crit Rate −100%, "Flawless Strategy" | She cannot crit; her numbers are planned, not lucky | She cannot gain Strength; Strength becomes Tide (rule 8) |
| Strategist of the Resistance, raised on treatises | She wins the fight before it starts | **Plan**: a card paid for now that the jellyfish carries out at the start of her next turn (rule 6) |
| Gorou, her general | He executes what she writes | Gorou's Personal is a Plan: play a copy of the last Companion she played (§7) |
| The Clouds Like Waves Rippling (C2) | Heals more on those under half HP | An Uncommon: under half HP, every card the jellyfish plays Mends her 2 |
| Water's Edge (C1) | Her basic attack ends with a fish | Water's Edge is the basic Attack |

Not used: water-walking, Orobashi (a boss-Rare name at most), C4 attack
speed.

## 4. The rules of the kit

Eight sentences. If a rule is not here, it is a card.

1. **The Bake-Kurage** is on the field for the whole combat. It holds
   **Tide**, a number from 0 that never resets on its own, and its
   **Memory**, a row of cards in the order they arrived.
2. **Tide** is added by her cards ("Tide +N"), and by 1 whenever a card of
   hers Exhausts.
3. **Remember**: when a card she owns Exhausts (her own or a Companion),
   the jellyfish remembers it, with its target and its choices. A card the
   jellyfish played is never remembered again.
4. **The replay**: at the start of her turn, if the Tide covers the front
   memory's price (3 per energy of its printed cost; a 0-cost card is
   free), the jellyfish pays it, plays the card, and forgets it. One a
   turn. A front card it cannot afford holds the row.
5. **Surge**: a card that says it makes the jellyfish play remembered cards
   from the front, paying each from the Tide, until it cannot; then the
   Tide is 0.
6. **Plan**: a card that says it is paid for now and not played now; it
   goes into the Memory at no price, and the jellyfish carries it out.
7. **Mend**: heal, never above the HP she entered the combat with. Only
   Uncommon-and-up cards Mend, and all of them Exhaust, so each Mends
   twice at most (once by her, once by the jellyfish).
8. **Flawless Strategy**: she cannot gain Strength; Strength she would gain
   becomes Tide.

**Garment** is a card state, not a rule: for a stated number of turns each
of her Attacks that hits Mends her 2. A remembered card keeps its target;
if the target is dead or gone the jellyfish picks a living one at random.
The one thing that fires by itself is the jellyfish's one replay a turn,
and that is what a summoned jellyfish does.

Persistent UI: the Tide number on the jellyfish, the row of remembered
faces beside it with each card's price, and the Garment turn count. The
memory strip already exists (EB-198, live-accepted on `0.2.1506+proto`).

**What leaves from draft 2:** Exert, the pulse and its budget, the
Priestess's "hold" verb, Surge as a damage number, Plan as a separate
queue. **What stays:** the jellyfish, Tide, Surge's name and job (cash),
Mend bounded at entry HP, Garment, Flawless Strategy, Hydro on every
Attack. **What returns from the shipped kit:** the Memory (your spec,
`review/ruled/kokomi-kurage-memory-2026-08-29.md` §11.1), with one door
instead of Muster's random one.

## 5. The contested thing

**What you let it remember, and in what order.** The row is first in,
first out, and the jellyfish plays one a turn. So the order you Exhaust
and Plan is the order the fight replays: a Salt Line queued before an
Ambush means Block next turn and the 12 the turn after; a High Tide
queued behind three Plans is fuel that arrives late. The Tide is the other
half: a row that outruns the Tide stalls, and a Tide with nothing queued
is wasted, so her Skills are split between feeding the jellyfish and
giving it something to do.

- **Remember or keep.** Exhausting a card is giving it to the jellyfish.
  Cleansing Tide Mends 6 now and 6 again in a turn or two; Salt Line is 7
  Block and 7 Block again. The price is the card's absence from her deck
  for the rest of the fight and its Tide price when it comes round.
- **Plan or play.** A Plan is the same card a turn late for the same
  energy, in exchange for the jellyfish carrying it out with no Tide and
  with the enemy's intent known.
- **Surge now or let it run.** The replay is one card a turn. Surge is the
  whole row as far as the Tide reaches, on the turn you choose, and it
  empties the Tide whether or not it reached the end. A full row and a
  deep Tide on the boss's big turn is the payoff; a Surge into a short row
  is a wasted Tide.

The cost is real in both directions because the jellyfish is slow: a card
you queue is a card that will not help you this turn, and a fight that
ends in two turns never pays for anything it remembered. The question she
answers every turn is the strategist's: what do I want done next turn,
and can the Tide pay for it?

**Calibration.** The Necrobinder's Osty is the shape: an always-out
creature the kit gives orders to, with cards that make it act. The
difference is that Osty has its own attacks and the jellyfish has none;
everything it does is one of her cards, so the jellyfish is exactly as
strong as the deck she wrote.

## 6. The three loops

### 6.1 Priestess — "feed, remember, surge" (the starter's plan)

- **A turn looks like:** Salt Line (7 Block, remembered), Kurage's Oath
  (Tide +4), Water's Edge; next turn opens with the jellyfish paying 3
  and raising 7 Block before the hand is played. Two turns of that, then
  Rising Tide Surges a row of three into the raider.
- **You draft:** Tidal Prayer (Tide +3, draw 1), Sea Spray (Deal 5, Tide
  +2), High Tide (Uncommon, Exhaust: Tide +8, so the jellyfish's replay of
  it is fuel), Undertow (the jellyfish plays the front memory now, paying;
  Block 3), Breaker (Deal 8, Surge), Song of Pearls (Power: each card the
  jellyfish plays is Tide +2), Nereid's Ascension (Uncommon, Exhaust: the
  Garment for 2 turns, and again when it comes round), Cleansing Tide
  (Uncommon, Exhaust: Mend 6).
- **The payoff moment:** a five-card row and a 15 Tide on the turn the
  boss winds up, Breaker Surges the lot: Block, a Mend, the Garment, an
  Ambush, and the 8 on top.
- **The decision every turn:** feed or queue. A Skill that raises the Tide
  keeps the row moving; a card that Exhausts gives the row something to
  do; Surge cashes both.
- **The Rare that breaks a rule:** *Sango Isshin* (Power): Mend that would
  go past her entry HP becomes Hydro damage to a random enemy. Rule 7's
  ceiling is gone, and a full bar is a weapon.
- **Weakness:** fights that end before the row pays, and a spike before
  the row is built.

### 6.2 Strategist — "the plan was written last turn"

- **A turn looks like:** two Plans and a Block, end turn, take the hit;
  next turn the jellyfish opens with a free 12 and a free 5 Block before
  the hand is played.
- **You draft:** Battle Plan (Plan: gain 2 energy), Ambush (Plan: deal 12
  to a random enemy), Read the Field (Block 3 now, Plan: Block 5), Feint
  (Deal 4, Plan: 8 to the same enemy), Contingency (Uncommon, Exhaust,
  Plan: Mend 6), Treatise (Power: each card the jellyfish plays draws 1),
  War Council (Uncommon, Plan: play the top two cards of the draw pile
  free).
- **The payoff moment:** the cultists' ramp lands on the turn her Plans
  do, and she wrote them a turn ago knowing the intent.
- **The decision every turn:** now or next turn. A Plan costs the same
  energy as its now-version and arrives a turn late with the information
  paid for; and a Plan at the front of the row is one the Tide never has
  to pay for, so a Strategist deck runs on a shallow Tide.
- **The Rare that breaks a rule:** *The Art of War* (Power): Plans also
  happen now. Rule 6's delay is gone.
- **Weakness:** intent changes, and the row jams behind a memory the Tide
  cannot pay, which a Strategist with no Tide cards will feel.

### 6.3 Commander — "Gorou, go"

The smallest loop until the companion layer proves itself (§7). Her cards
choose which companion the jellyfish plays again.

- **You draft:** Rally (Exhaust a Companion card from your hand; the
  jellyfish remembers it; Tide +2), Orders (Power: a Companion play is Tide
  +2), Vanguard (the next Companion this turn costs 0), Gorou's Personal
  (Plan: play a copy of the last Companion you played this turn), the
  Inazuma pool at its home weighting.
- **The payoff moment:** Raiden Rallied on turn two, and the jellyfish
  plays her again on turn three and once more in the Surge.
- **The Rare that breaks a rule:** *The General's Banner* (Power): the
  jellyfish plays two memories a turn. Rule 4's one is gone.
- **Weakness:** she cannot draft the army herself, and every companion in
  the row is one she chose to give up; Priestess and Strategist must each
  win without a single companion.

### 6.4 Bridges

- Undertow: the front memory now, paying. The Priestess's tempo and the
  Strategist's way to collect a Plan on the turn it was written.
- Contingency: an Exhaust Plan, so it Mends now-ish and again later.
- Orders: companions become Tide, so the Commander's row keeps moving.
- Change of Plans (Common, 0): forget the front memory, draw 1. The eject
  for a jammed row, in every loop.

### 6.5 Currencies, and which way they cross

- **Cards → the row** (Exhaust, Plan, Rally); **the row → plays** (the
  replay, Undertow, Surge).
- **Skills → Tide** (Oath, Tidal Prayer, Quiet Study, Coral Bulwark);
  **Exhaust → Tide** (rule 2); **Companions → Tide** (Orders); **the
  jellyfish's plays → Tide** (Song of Pearls).
- **Tide → plays** (the replay, Surge), **→ cards** (Reading the Tide:
  draw 1, plus 1 per 5 Tide).
- **The jellyfish's plays → cards** (Treatise), **→ HP** (The Clouds Like
  Waves, under half).
- **Damage dealt → HP** (the Garment), in chips.
- **Strength → Tide** (rule 8), which is how any shared Strength source in
  the mod reaches her without a card.

## 7. The companion layer, for her

One loop of three, never the starter's plan. Under the structure ruled
for Klee on 2026-09-01: Personals slot-sharing and one each, Gorou first
("Plan: play a copy of the last Companion you played this turn"); Inazuma
is her home nation, so the home weighting already shows her Sayu,
Shinobu, Thoma, Sara, Itto and Raiden, all rebuilt under R236. Stand-ins
with their own names in place of Inazuma Universals come from the
per-character workshop: Thoma's barrier as Block that feeds the Tide,
Shinobu's ring as a chip Mend on Exhaust, Sara's stormcall as a Plan.
Nothing here is authored. She has no tag; her readers, if any, read
"Companion."

The trap you named: the shipped kit converged on "spam Muster, random bad
companion cards go." Here no companion enters the row by chance or by
being played: the only door is Rally, which Exhausts one chosen Companion
card from her hand for a card and an energy, or a Companion that itself
says Exhaust. Every companion the jellyfish plays is one she picked.

## 8. The intended weakness, and how she survives anyway

**She is a turn slow, and her Block is the worst in the roster.** Coral
Guard is 5 for 1 and there are few Block cards in her pool; everything
good she does arrives at the start of the next turn, through the
jellyfish, one card at a time. Against a long fight she outbuilds anyone.
Against a fight that hits for 20 on turn two, or ends on turn two, she is
the character with the least between her and the hit and the least to
show for her setup.

| Defence | Trigger | Lore | Which loop |
|---|---|---|---|
| **Block** | Standard, scarce | She is not a fighter | All |
| **Salt Line** (starter, Exhaust) | 7 Block, and 7 again when it comes round | The tide line on the shore | Priestess |
| **Read the Field** (Common) | Block 3 now, Plan: Block 5 | The defence she wrote | Strategist |
| **Undertow** (Common) | The front memory now, and Block 3 | The wave that recedes | Bridge |
| **Contingency** (Uncommon, Exhaust) | Plan: Mend 6, twice at most | The fallback in the plan | Strategist |
| **Cleansing Tide** (Uncommon, Exhaust) | Mend 6 now, and again | Her own prayer | Priestess |
| **The Clouds Like Waves** (Uncommon Power) | Under half HP, each card the jellyfish plays Mends 2 | C2 | Comeback |
| **The Garment** (Uncommon, Exhaust) | Two turns of Attacks that Mend 2, twice at most | Nereid's Ascension | Priestess |

**Where the player feels it.** On the draft screen: Block cards are rare
in her pool and half her good cards say "next turn." On the map: a
two-turn hallway fight is a fight she wins without the jellyfish, so she
takes hallway chip like a character with a weaker deck than hers; elites
and bosses are where the row pays. Rest sites are hers because her entry
HP is the cap on every Mend in the fight after. She feels the missing
Block the way Ironclad feels the missing draw, and she feels the delay
the way the Defect feels an empty orb slot.

## 9. What fight one teaches

Starter deck, ten cards: Water's Edge ×3 (1 energy: 6 damage), Coral
Guard ×2 (1 energy: Block 5), Salt Line (1 energy: Exhaust, Block 7),
Kurage's Oath ×2 (1 energy: Tide +4), Rising Tide (1 energy: 4 damage,
Surge), Stolen Chapter (1 energy: Plan, draw 2).

Relic, **Tamanooya's Casket**: the jellyfish is on the field from the
start of every combat, and the first card it plays each combat costs no
Tide. It pays for the first replay: without it, fight one's Salt Line
comes back only if an Oath was drawn first; with it, the jellyfish acts on
turn two of every fight no matter what, which is the first thing the
player learns.

Turn one, fight one, the player sees: Attacks, Block, one Block card that
says Exhaust, a card that feeds the jellyfish, one card that says Surge,
one Plan. Playing Salt Line puts its face beside the jellyfish with a
price on it. Turn two opens with the jellyfish playing it: 7 Block before
the hand. Do a thing, the jellyfish does it again, is on the table with
nothing hidden, and the Plan and the Surge are the two things left to
try. Script A plays it out.

## 10. Failure modes, named

- **The spam.** Your trap: "spam Muster a million times, random bad
  companion cards GO." Closed five ways: nothing enters the row at random
  (Muster is gone; the doors are her own Exhaust cards, her Plans, and a
  Rally that Exhausts one chosen Companion); a card the jellyfish played is
  never remembered again; the jellyfish plays one a turn (two under one
  Rare); Surge reaches only as far as the Tide; and the row is first in,
  first out, so junk in front is a cost, not a resource.
- **The jam.** A front memory the Tide cannot pay holds the row. Kept on
  purpose, since it is the price of queuing what you cannot fund; Change
  of Plans at Common is the eject, and a Strategist row of Plans never
  jams because Plans have no price.
- **The infinite.** One replay a turn, replays never re-enter, prices are
  three per energy, and Surge empties the Tide. A long row slow-plays over
  many turns, which is the shape you asked for; EB-234 measured the old
  memory's queue at a 95th percentile of 9 and a worst of 31, and Surge is
  the new answer to a long row. A cap is a Balance number.
- **The doom clock.** Tide that grows every turn and pays once. Tide grows
  only by her cards, and it is spent every turn the jellyfish acts.
- **Companion-locked.** Two loops win without a companion.
- **Plans that never fire.** The Strategist's weakness, kept: a fight that
  ends on turn two paid for nothing.
- **Word salad.** Six keywords: Tide, Memory, Surge, Plan, Mend, Garment.
  Pick 7. "Remember" is the verb of Memory, not a seventh keyword.

## 11. The three-board test (turn five)

**Board one, the Priestess.** Two Axe Raiders, one at 9 and one at 20,
both intending 8. Row: Salt Line (price 3), Cleansing Tide (price 3). Tide
7. Hand: Water's Edge, Kurage's Oath, Breaker, Coral Guard, Sea Spray.
Right play: Sea Spray the 9 (dead, Tide 9), Breaker the 20 (8, then
Surge: Salt Line for 3, Cleansing Tide for 3, Tide 0), Coral Guard. She
ends at 12 Block with 6 Mended and the row empty; the raider hits for 8
into 12. Wrong play: Oath and hold, and the jellyfish plays Salt Line
alone next turn while the 20 keeps swinging.

**Board two, the Strategist.** A Cultist at 30, ramping, intending 6.
Row: Ambush (free), Read the Field's Plan (free). Tide 2. Hand: Feint,
Battle Plan, Water's Edge, Coral Guard, Stolen Chapter. Right play: Feint
(4 now, its 8 queued), Battle Plan (2 energy queued), Coral Guard. Next
turn opens with 12, 5 Block, 8 and 2 energy before a card is drawn, with
the Tide untouched; the Cultist dies to the first Attack. Wrong play:
Water's Edge and Coral Guard now, and the row waits a turn for nothing.

**Board three, the Commander.** Gremlin Nob at 40, Enraged, intending 14.
Row: Raiden's Universal (price 3). Tide 4. Hand: Rally, Vanguard, a Thoma
Universal, Water's Edge, Salt Line. Right play: Salt Line (7 Block,
queued behind Raiden), Vanguard, Thoma free (Block and Tide), and hold
Rally; the jellyfish plays Raiden next turn for 3, and the Nob's Enrage
never sees it, because the jellyfish's plays are not hers. Wrong play:
Rally the Thoma card for a second copy and eat the Enrage on two Skills.

## 12. Turn script A, fight one (Jaw Worm, 42 HP)

**Turn 1.** Hand: Water's Edge, Water's Edge, Salt Line, Kurage's Oath,
Stolen Chapter. The Worm intends 11. Play Salt Line (7 Block; its face
appears by the jellyfish, price 3), Kurage's Oath (Tide 4), Water's Edge
(6; Worm 36). Take 4. The player has seen the row and the Tide.

**Turn 2.** The jellyfish plays Salt Line for free (the relic): 7 Block
before the hand. Hand: Coral Guard, Water's Edge, Rising Tide, Kurage's
Oath, Coral Guard. The Worm intends 7. Rising Tide (4; Surge: the row is
empty, Tide 4 to 0; the player learns Surge wants a full row), Oath (Tide
4), Water's Edge (6; Worm 26). Take 0.

**Turn 3.** Nothing queued, the jellyfish waits. Hand: Salt Line, Stolen
Chapter, Water's Edge, Water's Edge, Coral Guard. The Worm intends 11.
Stolen Chapter (its face joins the row at no price: Plan), Salt Line (7
Block, queued behind it, price 3), Water's Edge (6; Worm 20). Take 4.

**Turn 4.** The jellyfish plays Stolen Chapter: draw 2. Hand of seven.
Tide 4. Water's Edge ×2 (Worm 8), Oath (Tide 8), Coral Guard. Take 2.

**Turn 5.** The jellyfish plays Salt Line for 3 (Tide 5): 7 Block. Water's
Edge, Rising Tide: Worm dead. Fight one taught: the row, the price, the
free first replay, a Plan, and one wasted Surge.

## 13. Defaults taken, and the things that are genuinely yours

Applied from the rework packet at their defaults, on your "I think that
could potentially work": direction A; Exert leaves the base loop; the
pulse is gone and Mend lives on Uncommon-and-up Exhaust cards; the starter
is Salt Line plus one Surge card. Draft 3's own picks:

1. **Plan's price.** (1) *Paid now in energy, free in the row* [default: a
   Strategist deck runs on a shallow Tide and never jams]. (2) Written for
   0 energy and priced in Tide like a memory.
2. **Surge's reach.** (1) *From the front, paying each, as far as the Tide
   goes; the rest of the Tide is lost* [default: Surge has a right size].
   (2) The whole row, free, then Tide 0.
3. **The jam.** (1) *An unaffordable front memory holds the row, and
   Change of Plans at Common ejects it* [default; your "blocks Memory until
   it's played"]. (2) An unaffordable front memory is forgotten at the end
   of her turn.
4. **The relic.** (1) *The first card the jellyfish plays each combat is
   free* [default: fight one always shows the replay]. (2) Start each
   combat at Tide 3.
5. **The Commander's door.** (1) *Rally-type cards Exhaust one chosen
   Companion from hand* [default]. (2) Every Companion play is remembered,
   which is the spam.
6. **The replay rate.** (1) *One a turn; The General's Banner makes it two*
   [default: your number]. (2) Two a turn as the base.
7. **Keyword budget.** (1) *Six: Tide, Memory, Surge, Plan, Mend, Garment*
   [default]. (2) Fold Garment into its one card: five.

Picks 6 and 7 are taken at their defaults unless you say otherwise. The
rest are design picks. Prices (3 per energy) and the pool's numbers are
the prototype's and err generous on purpose; Balance prices them.

## 14. What this document does not do, and two things to watch

- **The row's length.** EB-234's read of the old memory (a 95th percentile
  of 9, a worst of 31) is the number to re-measure: if rows routinely
  outrun the Tide, the price or the feed moves before anything else.
- **The Commander loop is only as good as the companion cards.** Its
  strength is measured against the R236 companions, and a weak Commander
  read before the Inazuma prototype is in the build is not a Kokomi
  defect.

It does not author the sheet, price a card, or claim a winrate. It does
not decide any Watatsumi relic beyond the Casket. It does not author a
stand-in or Gorou's Personal. "Entry HP" means the HP she walked in with,
which makes rest sites hers. Nothing here is a ruling.

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

## 16. What your run changed (draft 2 → draft 3)

- **The Memory is back, and her own cards go in.** Your 2026-08-29 spec
  (one replay a turn, three Tide per energy, 0-cost free, an unaffordable
  front card blocks, no cap) with Exhaust as the one door and Muster gone.
  Salt Line, the card you called barely better than a Defend, is the first
  thing the jellyfish does again.
- **Plan is a door into the same row,** not a second queue. Paid now, free
  later, same target.
- **Surge plays the row** instead of dealing a number. The Tide is fuel,
  not damage.
- **Exert and the pulse are gone.** You called one a tax and the other
  incomprehensible; both priced a bet that had no side worth taking. Her
  HP is her bar again, and healing is only the bounded Mend cards.
- **The calibration moved** from the Slime Boss to the Necrobinder's
  Osty: an always-out creature the kit gives orders to.
- **The keyword budget is the same six** with Memory replacing Exert.
