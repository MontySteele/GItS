Status: OPEN (draft 4 picks 1 to 7; the live Paper artefact through the Prototype build)

# Sangonomiya Kokomi: the brief, draft 4

Draft 4, 2026-09-02, on [USER]'s second thought about draft 3 (R239, in
the commit): the Tide stays as the fuel, but the jellyfish never spends it
by itself; Surge plays one card, the top of her exhaust pile, and pays its
price; and a card the jellyfish has played is a Tactic that never comes
back. Draft 3's row and its one-a-turn replay are gone, and the exhaust
pile is the memory. §17 lists what moved. Everything a build needs is in
§4, §6 and §9; the rest is the reasoning.

## 0. The test this brief has to pass

The Klee brief's seven: three boards (§11), one contested thing (§5),
fight one (§9, script A), borrowed systems (§4, §6.5), the rule each Rare
breaks (§6), what the relic pays for (§9), and lore (§3).

## 1. The promise

You are the Divine Priestess of Watatsumi, and you do not fight. You write
the orders, and the Bake-Kurage carries them out. What you have already
used is not gone: it is on the pile, and when you say the word and the
Tide is high enough, the jellyfish picks up the last thing you did and
does it again. Once. **Your exhaust pile is your book of tactics. The
jellyfish reads from the top, and the Tide is what it costs to read.
What you put there last, how high the Tide is, and when you say the word
is the whole game.**

In play: Kokomi's Exhaust cards are one-shots that come back one more
time, on the turn she chooses, through a Surge card, if the Tide can pay.
Her Skills raise the Tide; Exhausting anything raises it by one. A Plan is
an order she pays for now and the jellyfish carries out next turn. A
companion she Rallies is a companion the jellyfish will send in again.
Every card the jellyfish plays becomes a Tactic, spent for the fight.

**The obvious plan, from the starter:** Exhaust the Block, feed the Tide,
Surge it back.

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

Draft 2 made the bank a number Surge dealt once and priced every step in
HP and turns; your run and both seats did the arithmetic and it lost to
the basic attack. Draft 3 brought your Kurage's Memory back as a priced
row the jellyfish worked through by itself, one a turn; you read that as
"automatically spend to play one card per turn," which is energy cheating
with a timer on it. Draft 4 keeps the bank and the spend and puts the
spend in your hand: a Surge card, one replay, paid.

## 3. The lore audit

| Source | Fact | What it becomes |
|---|---|---|
| Kurage's Oath (Skill) | The Bake-Kurage sits on the field, hits on an interval, heals on an interval | The jellyfish is always out and holds the **Tide**; when a card tells it to and the Tide can pay, it plays a card from her exhaust pile (rules 1 to 3). Kurage's Oath is the starter's feed |
| Her "energy" | She tracks her own energy: duties drain it, doing what she likes refills it | Retired in draft 3. Her vitality is her HP bar, not a price |
| Highest base HP in the source game | Her vitality is her stat | The biggest HP bar in the roster, and the worst Block (§8) |
| Nereid's Ascension (Burst) | The Ceremonial Garment: her attacks heal while she wears it | **Garment**: a short window where her Attacks Mend a chip per hit |
| Sango Isshin (C6) | A heal on someone at 80%+ HP becomes Hydro damage | The Priestess Rare: Mend past her entry HP becomes the jellyfish's hit |
| Tamanooya's Casket (passive) | Casting the Burst keeps the jellyfish out | The relic: the jellyfish never leaves, and the first card it plays each fight costs no Tide |
| Crit Rate −100%, "Flawless Strategy" | She cannot crit; her numbers are planned, not lucky | She cannot gain Strength; Strength becomes Tide (rule 8) |
| Strategist of the Resistance, raised on treatises | She wins the fight before it starts | **Plan**: an order paid for now that the jellyfish carries out at the start of her next turn (rule 4); **Tactics** is what a carried-out order is (rule 5) |
| Gorou, her general | He executes what she writes | Gorou's Personal is a Plan: play a copy of the last Companion she played (§7) |
| The Clouds Like Waves Rippling (C2) | Heals more on those under half HP | An Uncommon: under half HP, every card the jellyfish plays Mends her 2 |
| Water's Edge (C1) | Her basic attack ends with a fish | Water's Edge is the basic Attack |

Not used: water-walking, Orobashi (a boss-Rare name at most), C4 attack
speed.

## 4. The rules of the kit

Eight sentences. If a rule is not here, it is a card.

1. **The Bake-Kurage** is on the field for the whole combat and holds
   **Tide**, a number from 0 that never resets on its own.
2. **Tide** is added by her cards ("Tide +N"), and by 1 whenever a card of
   hers Exhausts.
3. **Surge**: a card that says it makes the jellyfish play the top card of
   her exhaust pile (the card exhausted most recently) at no energy, with
   the card's own target and choices, paying its price from the Tide: 3
   per energy of its printed cost, a 0-cost card free. If the Tide cannot
   pay, the jellyfish does nothing and the rest of the card still happens.
4. **Plan**: a card that says it is paid for and Exhausted when played,
   doing nothing yet; at the start of her next turn the jellyfish plays it
   at no Tide price, unless a Surge already has.
5. **Tactics**: a card the jellyfish has played. When it would go to the
   exhaust pile, it leaves the fight instead. So every card comes back
   once, and only a card that returns it from the exhaust pile to her hand
   can earn it a second time.
6. **Mend**: heal, never above the HP she entered the combat with. Card
   Mends are Uncommon and up.
7. **Garment**: a state for a stated number of turns; while she wears it,
   each of her Attacks that hits Mends her 2.
8. **Flawless Strategy**: she cannot gain Strength; Strength she would gain
   becomes Tide.

Exhaust is the game's own keyword and the jellyfish's only door: nothing
enters the pile except by Exhausting, and the order of the pile is the
order she exhausted. A dead target is replaced by a random living one. The
one thing that fires by itself is a Plan at the start of her turn, which
she paid for in energy, never in Tide.

Persistent UI: the Tide number on the jellyfish; the top card of the
exhaust pile shown beside it, face up, with its Tide price, as "what it
will do next"; the Garment turn count; the Tactics tag on a card the
jellyfish has played. Nothing else.

**What leaves from draft 3:** the row as a second structure, the
one-a-turn replay, Surge as "play the row," the jam and its eject. **What
stays:** the jellyfish, the Tide and its feeds, the price at 3 per energy,
Surge's name, Plan, Mend bounded at entry HP, Garment, Flawless Strategy,
Hydro on every Attack. **What is new:** Tactics, your once-only tag, and
the exhaust pile as the memory.

## 5. The contested thing

**What is on top, how high the Tide is, and when you say the word.** The
jellyfish reads the last card she exhausted, at a price. So three things
are hers every turn: the order she exhausts in (Salt Line then Cleansing
Tide means a Surge now Mends 6 for 3 Tide and a Surge later Blocks 7 for
3); whether the Tide covers the top (a Blessing on top at 6 Tide is a
Surge that does nothing at 5, and two Oaths of feeding before it does);
and whether to Surge now at the top's value or feed first and Surge
bigger.

- **Exhaust it or keep it.** Her Exhaust cards are the good ones. Playing
  one puts it where the jellyfish can reach it, adds 1 to the Tide, and
  takes it out of her deck; the second play, when it comes, is final.
- **Feed or spend.** A Skill that raises the Tide is a turn's energy spent
  on next turn's Surge. A Surge with the Tide short is a Strike with a
  promise on it.
- **Surge now or wait.** The top card and its price are known. Surge it
  now, or play another Exhaust card first and Surge that instead, at the
  cost of the first one sliding under.
- **Plan or play.** A Plan is the same card a turn late for the same
  energy, no Tide, with the intent known, and it sits on top until it
  fires, so a Surge can collect it early for nothing.

The cost is real in both directions because nothing is free twice: every
card the jellyfish plays is a card gone from the fight, every Tide spent
on a small card is Tide not there for a big one, and every Surge card in
hand is one she could have used on a better top. The question she answers
every turn is the strategist's: what do I want done again, and have I
paid for it?

**Calibration.** Ironclad's Exhume (1 energy: return a card from the
exhaust pile to your hand) is the price anchor: a Surge is an Exhume that
also plays the card, for the card never coming back and a Tide price the
deck has to raise. Rising Tide (1 energy: Deal 4, Surge) is Exhume plus
half a Strike, gated twice.

## 6. The three loops

### 6.1 Priestess — "Exhaust it, feed, Surge it back" (the starter's plan)

- **A turn looks like:** Salt Line (7 Block, to the pile, Tide 1), Kurage's
  Oath (Tide 5), Water's Edge; next turn Rising Tide: 4 damage and the
  jellyfish raises the 7 again for 3 Tide, Salt Line leaves the fight.
  Two turns of that, then Watatsumi's Blessing goes on the pile and the
  Tide is fed to 6 for the Surge that Mends 12 and draws 2.
- **You draft:** Tidal Prayer (Tide +3, draw 1), Sea Spray (Deal 5, Tide
  +2), Deep Current (Deal 4 to all, Tide +1 per hit), Breaker (Deal 8,
  Surge), Undertow (Block 3, Surge), High Tide (Uncommon, Exhaust: Tide
  +8, so its replay is fuel), Song of Pearls (Power: each card the
  jellyfish plays is Tide +2), Nereid's Ascension (Uncommon, Exhaust: the
  Garment for 2 turns), Cleansing Tide (Uncommon, Exhaust: Mend 6).
- **The payoff moment:** Blessing on top and the Tide at 9 on the boss's
  wind-up: Breaker for 8, the jellyfish Mends 12 and draws 2 for 6 Tide,
  and the draw finds Undertow for the Cleansing Tide underneath.
- **The decision every turn:** what goes on top, and whether the Tide is
  there for it.
- **The Rare that breaks a rule:** *Sango Isshin* (Power): Mend that would
  go past her entry HP becomes Hydro damage to a random enemy. Rule 6's
  ceiling is gone, and a full bar is a weapon.
- **Weakness:** a deck that thins itself has no third play of anything;
  a long fight runs her out of tactics, and a fast one out of Tide.

### 6.2 Strategist — "the plan was written last turn"

- **A turn looks like:** two Plans and a Block, end turn, take the hit;
  next turn the jellyfish opens with a free 12 and a free 5 Block before
  the hand is played, no Tide spent, and both cards are Tactics.
- **You draft:** Battle Plan (Plan: gain 2 energy), Ambush (Plan: deal 12
  to a random enemy), Read the Field (Block 3 now, Plan: Block 5), Feint
  (Deal 4, Plan: 8 to the same enemy), Contingency (Uncommon, Plan: Mend
  6), Treatise (Power: each card the jellyfish plays draws 1), War Council
  (Uncommon, Plan: Surge twice).
- **The payoff moment:** the cultists' ramp lands on the turn her Plans
  do, and she wrote them a turn ago knowing the intent; or a Surge collects
  the Ambush on the same turn it was written, free, because it was on top.
- **The decision every turn:** now or next turn, and whether to leave the
  Plan on top for the jellyfish or Surge it early and leave the Tide for
  the card underneath.
- **The Rare that breaks a rule:** *The Art of War* (Power): Plans also
  happen now. Rule 4's delay is gone.
- **Weakness:** intent changes, fights that end before the Plans fire, and
  a shallow Tide, since a Strategist deck feeds it only by Exhausting.

### 6.3 Commander — "Gorou, go"

The smallest loop until the companion layer proves itself (§7). Her cards
choose which companion the jellyfish sends in again.

- **You draft:** Rally (Exhaust a Companion card from your hand; Tide +2),
  Vanguard (the next Companion this turn costs 0), Orders (Power: each
  Companion you play is Tide +2), Gorou's Personal (Plan: play a copy of
  the last Companion you played this turn), the Inazuma pool at its home
  weighting.
- **The payoff moment:** Raiden Rallied on turn two, on top at 3; Breaker
  on turn three: 8, and Raiden again.
- **The Rare that breaks a rule:** *The General's Banner* (Power):
  Companions the jellyfish plays are not Tactics. Rule 5's once is gone,
  for companions.
- **Weakness:** she cannot draft the army herself, and every companion the
  jellyfish plays is one she gave up from hand and paid the Tide for;
  Priestess and Strategist must each win without a single companion.

### 6.4 Bridges

- Undertow: a Surge that Blocks. The Priestess's defence and the
  Strategist's early collection.
- Moon's Reflection (Uncommon): put a card from your exhaust pile into
  your hand. The one door to a second replay, in every loop; and the way
  to move a card back to the top.
- Change of Plans (Common): choose a card in your exhaust pile and put it
  on top. Draw 1. The reorder, in every loop.
- Orders and Song of Pearls: companions and replays into Tide, so the
  Commander's and the Priestess's Surges keep paying.

### 6.5 Currencies, and which way they cross

- **Cards → the pile** (Exhaust, Plan, Rally); **the pile → plays** (Surge,
  a Plan's morning); **the pile → hand** (Moon's Reflection).
- **Skills → Tide** (Oath, Tidal Prayer, Quiet Study, Coral Bulwark);
  **Exhaust → Tide** (rule 2); **Companions → Tide** (Orders); **the
  jellyfish's plays → Tide** (Song of Pearls).
- **Tide → plays** (Surge), **→ cards** (Reading the Tide: draw 1, plus 1
  per 5 Tide).
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

The trap you named: "spam Muster a million times, random bad companion
cards GO." Here no companion enters the pile by chance or by being
played: the doors are Rally, which Exhausts one chosen Companion card from
her hand for a card and an energy, and a Companion that itself says
Exhaust; the jellyfish plays it only when a Surge card says so and the
Tide pays its price; and once it has, it is a Tactic and gone. Every
companion the jellyfish plays is one she picked, paid for, once.

## 8. The intended weakness, and how she survives anyway

**Her Block is the worst in the roster, and her deck eats itself.** Coral
Guard is 5 for 1 and there are few Block cards in her pool; her best cards
Exhaust, come back once through a Surge she has to draw and a Tide she has
to raise, and then leave. Against a fight of three or four turns she has
more plays than anyone. Against a fight that hits for 20 on turn two she
is the character with the least between her and the hit, and against a
long fight she is the character who runs out.

| Defence | Trigger | Lore | Which loop |
|---|---|---|---|
| **Block** | Standard, scarce | She is not a fighter | All |
| **Salt Line** (starter, Exhaust) | 7 Block, and 7 again on a Surge for 3 | The tide line on the shore | Priestess |
| **Read the Field** (Common) | Block 3 now, Plan: Block 5 | The defence she wrote | Strategist |
| **Undertow** (Common) | Block 3 and a Surge | The wave that recedes | Bridge |
| **Contingency** (Uncommon, Plan) | Mend 6 next turn | The fallback in the plan | Strategist |
| **Cleansing Tide** (Uncommon, Exhaust) | Mend 6 now, and again on a Surge for 3 | Her own prayer | Priestess |
| **The Clouds Like Waves** (Uncommon Power) | Under half HP, each card the jellyfish plays Mends 2 | C2 | Comeback |
| **The Garment** (Uncommon, Exhaust) | Two turns of Attacks that Mend 2, twice at most | Nereid's Ascension | Priestess |

**Where the player feels it.** On the draft screen: Block cards are rare
in her pool and half her good cards say Exhaust. On the map: hallway
fights are hers, since two plays of a Salt Line is 14 Block for 2 energy
and 3 Tide; elites and bosses are where the pile runs dry, the Tide runs
short, and the last Surge finds a Strike on top. Rest sites are hers
because her entry HP is the cap on every Mend in the fight after. She
feels the missing Block the way Ironclad feels the missing draw, and she
feels the thinning deck the way the Silent feels a discard pile she
cannot reach.

## 9. What fight one teaches

Starter deck, ten cards: Water's Edge ×3 (1 energy: 6 damage), Coral
Guard ×2 (1 energy: Block 5), Salt Line (1 energy: Exhaust, Block 7),
Kurage's Oath ×2 (1 energy: Tide +4), Rising Tide (1 energy: 4 damage,
Surge), Stolen Chapter (1 energy: Plan, draw 2).

Relic, **Tamanooya's Casket**: the jellyfish is on the field from the
start of every combat, and the first card it plays each combat costs no
Tide. It pays for the first Surge: without it, fight one's Salt Line
comes back only if an Oath was played first; with it, the first Surge of
every fight works whatever the Tide, which is the first thing the player
learns, and the second is that the next one has a price.

Turn one, fight one, the player sees: Attacks, Block, one Block card that
says Exhaust, a card that feeds the Tide, one card that says Surge, one
Plan. Playing Salt Line puts its face beside the jellyfish with a 3 on it
and the Tide ticks to 1. Turn two, Rising Tide: the jellyfish plays Salt
Line for free, 7 Block, and Salt Line is gone. Exhaust it, feed, Surge it
back, is on the table with nothing hidden, and the Plan is the one thing
left to try. Script A plays it out.

## 10. Failure modes, named

- **The spam.** Your trap. Closed five ways: nothing enters the pile at
  random (Muster is gone; the doors are Exhaust, Plan and Rally); the
  jellyfish plays only when a Surge card or a paid Plan says so, one card
  per Surge; every Surge pays the Tide; a card the jellyfish has played is
  a Tactic and leaves; and Moon's Reflection, the only second chance,
  costs a card and an energy per card.
- **Energy cheating.** Your other word for it. Nothing the jellyfish does
  is automatic and unpaid: a Surge is a card, an energy and the Tide for
  one play of a card she already paid for once, and the card is gone
  after; a Plan is paid in energy the turn before. Battle Plan (pay 1 now,
  2 next turn) is the one net-positive energy card and it is a Plan, so it
  is a turn late and a Tactic after.
- **The empty pile, the short Tide.** A Surge with nothing exhausted, or
  a top it cannot pay for, plays nothing and the card's other half still
  happens. Kept: the top card and its price are on screen, and the blind
  page prints both.
- **The wrong top.** A Strike exhausted by an enemy's effect on top of her
  Blessing. Change of Plans is the reorder; otherwise it is a real cost
  and the Priestess feels it.
- **The doom clock.** Tide that grows every turn and pays once. Tide grows
  only by her cards, and it is spent every time she says the word.
- **Companion-locked.** Two loops win without a companion.
- **Plans that never fire.** The Strategist's weakness, kept.
- **Word salad.** Six keywords: Tide, Surge, Plan, Tactics, Mend, Garment;
  Exhaust is the game's. Pick 7.

## 11. The three-board test (turn five)

**Board one, the Priestess.** Two Axe Raiders, one at 9 and one at 20,
both intending 8. Exhaust pile, top first: Cleansing Tide (3), Salt Line
(3). Tide 7. Hand: Water's Edge, Breaker, Undertow, Sea Spray, Coral
Guard. HP 52 of 80. Right play: Sea Spray the 9 (dead; Tide 9), Breaker
the 20 (8; the jellyfish plays Cleansing Tide for 3: Mend 6, Tide 6),
Undertow (3 Block; the jellyfish plays Salt Line for 3: 7 Block, Tide 3).
Ten Block against 8, 6 Mended, the pile empty. Wrong play: Breaker first
and Sea Spray second, which puts Sea Spray on top and spends the Undertow
on a Strike.

**Board two, the Strategist.** A Cultist at 30, ramping, intending 6.
Pile, top first: Ambush (a Plan, free), Read the Field's Plan (free). Tide
2. Hand: Feint, Battle Plan, Rising Tide, Coral Guard, Stolen Chapter.
Right play: Rising Tide (4; the jellyfish plays Ambush now, free: 12;
Cultist 14), Feint (4 now, its 8 written; Cultist 10), Coral Guard. Next
turn opens with Read the Field's 5 Block and Feint's 8: dead, and the
Tide never moved. Wrong play: leave Ambush for the morning and take the
ramped hit first.

**Board three, the Commander.** Gremlin Nob at 40, Enraged, intending 14.
Pile, top first: Raiden's Universal (3). Tide 4. Hand: Breaker, Vanguard,
a Thoma Universal, Water's Edge, Salt Line. Right play: Breaker (8; the
jellyfish plays Raiden for 3: her Universal's damage again; the Nob's
Enrage never sees it, because the jellyfish's plays are not hers),
Vanguard, Thoma free. Wrong play: Salt Line first, which puts 7 Block on
top of Raiden and the Breaker buys Block.

## 12. Turn script A, fight one (Jaw Worm, 42 HP)

**Turn 1.** Hand: Water's Edge, Water's Edge, Salt Line, Kurage's Oath,
Stolen Chapter. The Worm intends 11. Play Salt Line (7 Block; it Exhausts,
its face appears by the jellyfish with a 3 on it, Tide 1), Water's Edge
×2 (Worm 30). Take 4. The player has seen the pile's top and its price.

**Turn 2.** Hand: Coral Guard, Water's Edge, Rising Tide, Kurage's Oath,
Coral Guard. The Worm intends 7. Rising Tide (4; the jellyfish plays Salt
Line for free, the relic: 7 Block; Salt Line is a Tactic and gone; Worm
26), Kurage's Oath (Tide 5), Water's Edge (6; Worm 20). Take 0.

**Turn 3.** Hand: Stolen Chapter, Water's Edge, Water's Edge, Coral Guard,
Kurage's Oath. The Worm intends 11. Stolen Chapter (Plan: it goes on top
at no price, Tide 6), Kurage's Oath (Tide 10), Water's Edge ×2 (Worm 8).
Take 11. The player has learned that a Plan waits on top for the morning.

**Turn 4.** The jellyfish plays Stolen Chapter: draw 2, hand of seven,
Stolen Chapter is a Tactic. Water's Edge ×2: dead, with the Tide at 10 and
nothing on the pile, which is the third lesson: a fed Tide with an empty
pile was wasted, and next fight the Salt Line goes on late.

## 13. Defaults taken, and the things that are genuinely yours

Applied on your note: the Tide stays and nothing spends it but a card you
play; Surge plays one card, the top of the exhaust pile, and pays its
price; a card the jellyfish has played carries a once-only tag. Draft 4's
own picks:

1. **The tag's name.** (1) *Tactics* [default: yours; "her book of
   tactics" is the pile, and a Tactic is an order carried out]. (2)
   *Executed*, which says the rule in the word. (3) *Spent*.
2. **The short Tide.** (1) *A Surge the Tide cannot pay plays nothing, and
   the card's other half still happens* [default: legible, and the price
   is on screen]. (2) It plays the top card anyway and the Tide goes to
   0, a discount for the desperate.
3. **Plan.** (1) *Paid and Exhausted now, played by the jellyfish next
   morning at no Tide, on top until then so a Surge can collect it early*
   [default]. (2) Plan cards are Surge-only: they never fire on their own
   and cost no Tide when Surged.
4. **The relic.** (1) *The first card the jellyfish plays each combat costs
   no Tide* [default: fight one's first Surge always works]. (2) Start
   each combat at Tide 3. (3) Every card the jellyfish plays Mends her 1.
5. **The second chance.** (1) *One Uncommon, Moon's Reflection, returns a
   card from the exhaust pile to hand* [default: your "unless a Skill
   draws the card back"]. (2) None; once means once.
6. **The replay's price.** (1) *3 per energy, 0-cost free* [default: your
   number from the Memory]. (2) 2 per energy, 0-cost 1, so nothing is
   ever free and cheap cards are the cheap replays.
7. **Keyword budget.** (1) *Six: Tide, Surge, Plan, Tactics, Mend, Garment*
   [default]. (2) Fold Garment into its one card: five.

Picks 6 and 7 are taken at their defaults unless you say otherwise. The
rest are design picks. The pool's numbers are the prototype's and err
generous on purpose; Balance prices them.

## 14. What this document does not do, and two things to watch

- **How often the top is the wrong card, and how often the Tide is
  short.** Enemy effects that Exhaust her cards, her Strikes never
  Exhausting, and a Strategist deck that feeds nothing decide whether
  Change of Plans and the Oaths are bridges or necessities; the seats'
  records will say how many Surges hit a card the player did not choose,
  and how many played nothing.
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

- **The Memory came back, and her own cards went in.** Your 2026-08-29
  spec (one replay a turn, three Tide per energy, 0-cost free, an
  unaffordable front card blocks, no cap) with Exhaust as the one door and
  Muster gone.
- **Plan became a door into the same row,** not a second queue.
- **Surge played the row** instead of dealing a number; the Tide became
  fuel.
- **Exert and the pulse went.** A tax and an incomprehensible chip.
- **The calibration moved** from the Slime Boss to the Necrobinder's Osty.

## 17. What your second thought changed (draft 3 → draft 4)

- **The jellyfish spends nothing by itself.** Your "we still want the
  system we're fueling, we just don't want automatically spend to play one
  card per turn." The one-a-turn replay is gone; the Tide is spent only
  when a Surge card you play says so.
- **Surge plays one card, the top of the exhaust pile, at its price.**
  Your "Surge just plays the top card from the Exhaust pile." The row is
  the pile itself, so there is no second structure, and no free plays:
  "play a card for free is already built-in energy cheating."
- **Tactics.** Your once-only tag: a card the jellyfish has played leaves
  the fight instead of returning to the pile, and only a card that returns
  it to hand earns a second replay.
- **The calibration moved** to Ironclad's Exhume, the price of reaching
  into the exhaust pile.
- **The name.** You asked for a lore-compliant rename of "Memory"; draft 4
  needs no name for the mechanic, since the exhaust pile is the game's own
  and the Tide already has one, and the tag takes yours. Pick 1.
