# Four-kit design review: a fresh read (2026-10-01)

**Ask ([USER], 2026-10-01):** "a long-form general review of the project and
characters (strengths and weaknesses of each design, what you like and
dislike, personally ... and areas for improvement, either mechanically or to
fit the lore of the character) ... And then a more tailored review on why the
playtesters keep dying. My suspicion is that we're not allowing for the
correct kind of lategame act 3 scaling that basegame characters rely on ...
at least on the defense side, but I could be completely wrong on that."

Written by a second main session (Fable) on [USER]'s Mac, with no part in the
passes it reviews. Longer than the usual two pages because the ask was
long-form. Picks are at the end; everything else is input to the passes the
Opus session already has queued.

**What I read:** `STATE.md`; the four briefs and their papers in
`review/active/`; every offered row in `docs/prototype-surface.yaml`; the
seat records of 2026-09-26 to 2026-10-01 in `review/records/`. **What I did
not have:** the raw seat transcripts (gitignored, on the playtest machine).
Base-game claims come from the only extract on this machine, an August one
of Ironclad and Silent (`../GItS-parity/game_ref/ironclad.json` and
`silent.json`), so they miss the other three characters and any card
changed since.

**What I ran:** five scratch probes on the tier-0 engine (§7). They are
instrument readings on stock pilots, not registered cells, and nothing here
is quotable as balance.

## 1. The short version

**Revised the same day against the raw run records (§2.8).** Items 1, 3
and 4 changed: Kokomi's problem is damage in the boss fight, not HP lost in
hallways, and the picks were re-ordered to match.

1. **"Block deficit" is three different problems under one name.** Kokomi
   cannot kill an act-1 boss fast enough: her seats dealt 8 to 15 damage a
   turn where base Ironclad and Silent dealt 20 to 22, while taking *less*
   per turn than Ironclad did (§2.8).
   Furina's shield cannot grow past about four times what she feeds it each
   turn. Varka's scaling Block reads one element's Oath, and most of his
   drafts split Oath across four. Klee is fine.
2. **The death turn is the same sentence in all four kits: "no Block card in
   hand."** That is a hand-composition problem, not a Block-per-Energy
   problem, and bigger Block cards do not fix it. The base game fixes it
   with Block that does not need to be drawn. Klee has that; the other three
   have little of it.
3. **[USER]'s act-3 theory is half right.** It holds for Furina (by
   construction) and for Varka in any deck that splits its Oath. It is the
   wrong act and the wrong side for Kokomi: she dies in act 1, and what
   fails to scale is her damage. Her one scaling engine, the Casket, pays
   once a fight and sat dead at a count of 10 to 13 in the boss fights she
   lost.
4. **Kokomi is the only kit whose mechanic starts every fight at zero and a
   turn late.** The other three were each given a turn-one grant (Usher,
   the Fang's element, an Innate Jumpy Dumpty and a Spark). In the sim, a
   Plan already written when combat opens roughly halves her hallway HP
   loss. The run records do not make this her binding problem, though: her
   hallway losses match the base game's, so the opening Plan is now a
   second step, not the first (picks 1 and 2).
5. **The two kits that work make defence a by-product of the engine** (Klee's
   Mines and Sparks, Furina's front performer). The two that struggle buy
   defence separately from the engine (Kokomi, and Varka in a split deck).
6. **The pool outran the instrument.** Kokomi went 44 to 78 cards between
   2026-09-29 and 2026-10-01, on two seats a round, while the ten-card starter plus Commons could
   not clear act 1. I would stop adding cards to her until the chassis does.

## 2. Why the seats die

### 2.1 Three problems, one name

| Kit | Where it dies | What the records say | The actual problem |
|---|---|---|---|
| Kokomi | Act-1 boss, 4 of 4 on 2026-10-01 | reached the boss at 34 and 51 of 80; "about 10 HP lost per fight" | attrition in short fights, then too little damage for the boss |
| Furina | Act-3 boss (three Opus runs on 2026-09-26, one of two Sonnet seats on 2026-10-01) | "60 incoming at 26 HP"; the front "soaks about 3 per hit" | a shield that cannot scale, and Block cards kept weak on purpose |
| Varka | Act-3 boss, phase 2 | "13 to 14 Block a turn against 40 to 60 incoming" | scaling Block reads one element's Oath; most drafts hold four |
| Klee | Act-3 elites and bosses, with two wins in five | "a single big hit with no Block in hand" | none structural; her intended weakness |

Sources: `three-kit-round-2026-10-01.md`, `kokomi-pool-round-2026-10-01.md`,
`furina-pool-round-2026-10-01.md`, `klee-later-acts-2026-09-26.md`.

One caution on reading seat complaints. A seat that dies always reports
Block as short, because death is unblocked damage. The base Ironclad seat
died at the act-3 boss too, and four of five Opus base-game runs did
(`control-round-2026-09-26.md`). So "died at the act-3 boss short of Block"
does not separate our kits from the base game. Dying in act 1 does, and so
does HP at the boss door, which the records carry only for Kokomi. §8 asks
for that number on every round.

### 2.2 The death turn: no Block card in hand

All four kits' records use the same words for the killing turn:

- Klee: "Both deaths in real runs came from a single big hit with no Block
  in hand."
- Kokomi: "had no Block card in hand on the elite's killing turn."
- Furina: "Every near-death and the act-3 death came on turns with no Block
  card in hand."
- Varka: "died with no Block card in hand on the turn it needed 40."

This is arithmetic, not bad luck. A 30-card deck with six Block cards draws
a five-card hand with none of them about 30% of the time (C(24,5) / C(30,5));
with eight Block cards it is still 18%. Every act-3 deck has a dead hand
every few turns, and raising a Block card from 8 to 11 changes nothing on
that turn.

The base game does not solve this with its ordinary Block cards either.
At one Energy its rates are no better than ours: Shrug It Off is 8 and
True Grit 7, Backflip 5, Survivor 8, against Coral Bulwark's 8, Shell of
Sanctuary's 9 and a starter Knight's 8. (It does have big two-Energy Block
cards that we lack; §2.7.) It solves it with **defence that is not in the
hand**:
Powers that pay every turn, Block that carries over, a multiplier on every
Block card, and HP back between fights. From the extract:

- **Ironclad:** Feel No Pain, Stone Armor and Colossus at Uncommon;
  Barricade and Juggernaut at Rare; Burning Blood's 6 HP after every fight.
- **Silent:** Anticipate (0 cost, Dexterity) and Dodge and Roll (Block next
  turn) at Common; Footwork (Dexterity) and Blur at Uncommon; Abrasive and
  Malaise at Rare; a 0-cost Weak in the starter.

None of our four kits has a Dexterity source of its own (the one in the
sheet is Gorou's companion card), and none heals between fights.

The same census on our kits, counting only defence that works on a hand
with no Block card in it:

| Kit | Off-hand defence | Reachable from the starter? |
|---|---|---|
| Klee | Mines (rule 6); Grounded, Look Out!, Sit Tight and Blast Shield, which returns to hand (U); Dodoco (R); Sparks buy Block without Energy | Yes: Jumpy Dumpty leaves Mines |
| Furina | the front performer's bar; Usher's 3 Block a turn; Pneuma (R); Sigewinne (U) | Yes, but small and capped (§5) |
| Varka | Oath of the Knights, Windborne Resolve (U); Oathbound Aegis, Dawn Wind's March (R); the Hydro Swirl's 3 Block. Three of the five pay only on the current element | Only on a Barbara start |
| Kokomi | a Block Plan written the turn before; Kurage Canopy (U); Watatsumi's Grace (R) | Only since the open-Plan rule, and only Kurage's Oath's 6 |

That table ranks the kits in the order the seats do. It is also my answer
to "what kind of scaling": not higher numbers on Block cards, but one
engine-native source of off-hand defence per kit, reachable at Common or
from the starter. §4 to §6 name one for each.

### 2.3 [USER]'s act-3 scaling theory, kit by kit

- **Furina: yes.** Rule 12 takes a quarter of every bar each turn, so a bar
  settles where the fade equals the income: about four times what she adds
  to it each turn. Feeding the front 3 a turn holds it near 12. Test
  Subject's phase 2 adds 30, 40, 50 and 60. Her Block cards are held down by
  ruling ("Keep her Block cards generally weak but her Spend cards strong"),
  so nothing on her defensive side grows with the run.
- **Varka: yes for the decks most drafts make.** The defence probe
  (provenance note, "Varka defence, 2026-10-01"), Block over incoming:

  | Deck | Act-3 elite | Act-3 boss |
  |---|---|---|
  | mono Hydro | 1.07 | 1.49 |
  | mono Pyro, Cryo, Electro | 0.68 to 0.71 | 1.03 to 1.05 |
  | default drafter | 0.60 | 0.80 |
  | gale, muster | 0.53 | 0.65 to 0.66 |

  A focused deck scales fine. The default drafter ends with Oath in all
  four elements in 73% of runs (`varka-defence-2026-10-01.md` §1), and so
  will most players; that deck, and the Gale and Muster decks, do not.
- **Kokomi: no.** She dies before scaling matters. Her problem is §2.4.
- **Klee: no.** Sparks buy Block and Bombs convert to it; one seat won on
  "Blast Shield on Sparks".

### 2.4 Kokomi: a turn behind, every fight

*Written from the sim before the raw records arrived. §2.8 corrects it:
the delay is real, but the place it costs her is the boss fight, not the
hallways.*

Plan pays a turn late. In a three- or four-turn hallway fight that is a
quarter to a third of the fight, and the enemies get one more swing than
they would against a deck that hits now. [USER]'s own run said it before any
seat did: "a lot of chip hits over time adding up ... things didn't die fast
and got to Strength buff themselves."

What the kit pays for the wait is thin. The halves rule (brief §3) removed
"the same effect, bigger", so a Plan line is priced at the going rate, not
above it: Kurage's Oath plans 7 to ALL for 1, and Deep Current deals 7 to
ALL for 1 now. The only wage for waiting is the Casket's count, which pays
once a fight, later.

Every other kit was handed something on turn one: Furina opens with Usher
at 3 Fanfare, Varka's Fang sets his element and deals him Four Winds'
Ascension, Klee's Jumpy Dumpty is Innate and she starts with a Spark.
Kokomi's relic hands her a payoff (Open the Casket) and no head start.

The probes agree (§7 for method and caveats):

- **Her starter is in family; her fights are long.** Starter against act-1
  hard fights: Kokomi 6.4 turns and 16.5 HP lost; Klee 4.3 and 14.0; Varka
  4.6 to 5.2 and 11.5 to 12.5; Furina 6.3 turns but 9.7 HP, because Usher
  soaks. With nine random picks she is still the slowest (6.4 turns) and
  loses the most (14.2).
- **On the same stylised act 1, Varka's default drafter wins 23%
  (provenance note, "Varka defence") and Kokomi's wins 0%.** Her run ends at
  the first elite 79% of the time.
- **A Plan already written at combat start is worth more than Block.**
  Emulated as Kurage's Oath's Plan line carried out on turn one, with
  starter plus nine drafted picks at full HP:

  | Build | Easy fight, HP lost | Hard fight, HP lost | Elites won | Act-1 bosses won |
  |---|---|---|---|---|
  | as built | 8.5 | 13.2 | 73% | 72% |
  | opening Plan | 4.3 | 9.7 | 83% | 89% |
  | Kurage Canopy 2 from turn one (the withdrawn shield, for scale) | 8.4 | 12.0 | 76% | 78% |

- **The opening Plan and a small heal multiply.** Stylised act 1, 400
  seeds: reaching the boss goes 0% as built, 4.5% with the opening Plan,
  0.5% with a heal of 1 per Plan (up to 6) after each fight, 16.5% with
  both, 24% with the opening Plan and a flat 6.

### 2.5 What I checked and ruled out

- **Pool dilution.** A seat on the 48-card pool reached the act-3 boss
  (`kokomi-feed-round-2026-09-29.md`); all four seats on 78 cards died in
  act 1. I expected the 30 added Uncommons and Rares to have thinned her
  act-1 drafts. The sim says no: decks drafted from the 78 and from its
  40 pre-expansion survivors fight act-1 elites and bosses the same (74%
  and 74% against 77% and 72%). The seats' drop is either the bosses rolled
  or noise, and the raw records would say which (§8).
- **The starter.** It is not weak. Against act-1 hallways it loses less HP
  than the sim's Ironclad starter (9.7 against 13.1 in easy fights).

### 2.6 How much is the harness?

Some, and it is not all "the seats' fault". Three things are mixed:

- **Priors.** Sonnet has read a decade of Slay the Spire strategy; the base
  seat knew to stack poison. It has read nothing about Plans.
- **Text the kits make hard.** Either/or lines read as both (Kokomi), Spends
  that silently play the plain side (Furina), an element lost without notice
  (Varka). Each cost HP in the records, and each will cost a new human
  player the same HP. That share belongs to the kits.
- **The sim's pilot.** In my per-card probe at least six Kokomi cards
  produced results identical to the digit, which means the stock pilot
  never played them (Change of Plans, Coral Tithe, Moon's Reflection, Read
  the Field, What the Tokoyo Returns, Kelp Wall). The sim reads her tempo
  honestly; it cannot read her cards. `BACKLOG.md` already says so for the
  status batch.

### 2.7 Read against the Opus defence audit (added the same day)

[USER] shared the Opus session's defence audit after this paper was
drafted; it is not in the repo at this commit. Its Ironclad and Silent
counts check against the local extract (three and two cards of 10+ Block;
Piercing Wail and Malaise for Silent's Strength loss). It agrees with §2.1
that density is not the problem (Kokomi 32% and Varka 33% of the pool
against the base game's 25%), and it shows two gaps this paper missed:

- **No kit has an answer to one big hit.** Cards giving 10 or more Block
  outright: 2 to 4 for each base character, and 0, 1, 0 and 1 for Klee,
  Kokomi, Furina and Varka. Blood Wall is 16 at Common. My "rates are no
  better than ours" held only at one Energy.
- **No kit can lower an enemy's Strength.** The base five have 1, 2, 0, 1
  and 4 sources; ours have none. All three act-3 deaths on 2026-10-01 were
  to Test Subject's phase 2, which adds 10-damage hits (3, then 4, 5, 6).
  Strength loss is the base game's answer to exactly that attack, since it
  comes off every hit, where Weak takes a quarter and Block is spent by
  the second hit.

One reading ties the audit and §2.2 together. The audit's "total flat
Block in the pool" row is 61 to 101 for the base five and 25 to 85 for
ours, with Kokomi at 50 across 15 Block cards. Our Block is not missing;
it is **conditional on the engine** (the Casket's count, Plans waiting,
Oath, Fanfare, a Bomb to give up), and every one of those starts each
fight at or near zero. Base-game Block mostly works on turn one.

Where I read it differently from the audit:

- **Kokomi, "no card change is indicated".** Agreed on cards, and §4 says
  freeze the pool. But "draft and timing" undersells it: the probes put the
  loss in tempo, and the opening Plan (pick 2) is a rule, not a card.
- **Furina, "no action".** Right for now, since [USER]'s run on the rules
  pass comes first. But her ten lasting defences are one mechanism counted
  ten times, and the fade caps it (§2.3). She has the least flat Block, no
  big-hit card and no Strength loss, and she died to the multi-hit. A
  Strength-loss Spend on Commanding Gaze ("Spend 3: ALL enemies lose
  Strength this turn instead") is the most direct answer in §5's shape,
  and an Archon's stare is the right voice for it.
- **Klee.** The audit is more worried than §3 is, and its point stands:
  her gap is a whole kind of threat, not a rate, and "fine" was too quick.
  I would still hold her. It is the weakness the brief chose ("she cannot
  block on demand"), her big-hit answers cost a Bomb on purpose (Favonius
  Escort, Sorry, Jean...), and she has the best results of the four. If
  the status-package round shows another act-3 death to one big hit, HP
  (62) is a cheaper lever than a Weak card that has no voice in her kit.

### 2.8 Read against the raw run records (added the same day)

[USER] sent the save-file histories and seat records for ten runs: the
four Kokomi act-1 deaths (`w8-lane3`, `w8b-lane3`, `w9-lane1`,
`w9-lane2`), the two Kokomi seats on the open-Plan build (`w11-lane1`,
`w11-lane2`), the two base runs and the two Varka runs. They are not in
the repo. Oath by turn was not recorded and deck lists carry no upgrade
marks. The records change this paper's reading of Kokomi and of Varka.

**Kokomi's hallways are in family. Her boss fights are not.**

| Act-1 normal fights | Fights | HP lost per fight |
|---|---|---|
| Kokomi, four pre-rule seats | 26 | 11.6 |
| Base Ironclad | 6 | 11.7 (5.7 after Burning Blood) |
| Base Silent | 6 | 10.7 |
| Varka, two seats | 12 | 4.3 |

| Act-1 boss fight | HP at the door | Turns | Damage dealt per turn | Damage taken per turn | End |
|---|---|---|---|---|---|
| Kokomi `w9-lane2`, Lagavulin Matriarch 222 | 71 of 80 | 13 | 11 | 5.5 | died, boss at 78 |
| Ironclad, Lagavulin Matriarch 222 | 74 of 80 | 11 | 20 | 6.2 | won at 6 HP |
| Kokomi `w9-lane1`, Ceremonial Beast 252 | 55 | 13 | 15 | 4.2 | died, boss at 53 |
| Kokomi `w8b-lane3`, Soul Fysh 211 | 49 | 17 | 8 | 3.0 | died, boss at 68 |
| Silent, Waterfall Giant 240 | 85 | 11 | 22 | 4.9 | won |
| Varka, Waterfall Giant 240 and Vantom 173 | 80 and 68 | 6 and 7 | 40 and 25 | 0.5 and 3.1 | won both |
| Kokomi `w11-lane2`, Waterfall Giant 240 | 77 of 101 | 12 | 22 | 7.7 | killed it on turn 11, died to its Death Blow |
| Kokomi `w11-lane1`, Waterfall Giant 240 | 80 | 6 | 40 | 7.3 | won |

The same boss, the same HP at the door: Ironclad won in 11 turns and
Kokomi died on turn 13 with a third of it left, having taken less damage
each turn than he did. She does not lose these fights on Block. She loses
them on length. That overturns §2.4's "bleeds out in hallways" (the sim's
stock pilot plays her hallways worse than a seat does) and §1's old item
1, and it qualifies the audit's "draft and timing": `w9-lane1` held eight
Block cards in twenty and Orichalcum, and `w9-lane2` walked in nearly
full.

**Why the damage is low: the Casket pays once.** Four of six records say
the same thing about the boss fight:

- "at the boss the count reached 10 and was dead weight after round 4"
  (`w8b-lane3`);
- "a long fight gave the Casket many Plans but one cash-in" (`w9-lane2`);
- "Casket reached 13 at death ... a dead number" (`w11-lane2`);
- "it never became an engine because I only Opened it for 1-4 Str"
  (`w8-lane3`).

Every seat opens it at 1 to 4, because Strength now beats Strength later
in a short fight, and then the relic is finished. So in a 13-turn boss
fight her only scaling is +2 or +3 Strength from turn 3. Ironclad had two
Perfected Strikes by then and Silent had poison. My sim cannot read this:
in a no-Exhaust trial its pilot ended act-1 boss fights at about 3
Strength, so it carries out a handful of Plans where a seat's count
reached 13.

**The open-Plan rule did nothing either seat could use.** About 57 chooser
screens across the two `w11` seats and one flip, which its seat called a
mistake. "The chooser was a confirm, not a decision." The Plan line is the
bigger number by construction, so it is nearly always right. The seat that
cleared two acts did it with a Cryo companion: Kaeya onto her Hydro for
Frozen, then Shatter, and Clorinde for 20 to 40. That is the Hydro pillar
working for the first time (§4, lore), not the rule. Both `w11` seats also
met Waterfall Giant, the boss base Silent and Varka beat, where the four
earlier seats met four others; boss identity is a confound a fixed seed
removes.

**Seat testimony about offers is unreliable; the save file is not.** The
round record says the rewards "rarely offered Block". The histories show
`w8b-lane3` declining Coral Bulwark three times and Tide Wall once, and
`w8-lane3` declining Coral Bulwark and Bubble Ward and then paying to
remove a Defend. The audit is right that Block was on offer and not
taken. The boss table says taking it would not have been enough.

**§2.2 holds up.** The base decks that reached the act-3 boss each carried
two off-hand defensive Powers (Ironclad: Juggernaut+ and Crimson Mantle;
Silent: Afterimage and Footwork). Of the two Varka decks one had none and
one took Oathbound Aegis two floors before the boss.

**Varka: in family, and my guard-mode idea is withdrawn.** His act-3
deaths look like the base game's: one seat reached Test Subject at 51 of
87 and drew no Block on the 60-damage turn; the other went in at full,
raced, and fell one turn short with the boss near 63 of 200. Base Ironclad
died to his act-3 boss from 39 HP and Silent won hers on about 3. The
records also put his Oath at 5 to 8 in act-3 fights, not the 35 to 50 an
earlier round saw. At that count every "half your total Oath" reader is a
flat card (Gale Mantle gives 8), and the guard mode I proposed in §6 would
give about 7 Block against 60. Oath is the wrong axis for his defence in
fights of ordinary length. Test Subject's Enrage also taxes every Skill,
and all his Block is Skills. The other end deserves a note for Balance:
his act-1 hallways cost 4 HP a fight against the base game's 11, and both
seats reached the act-1 boss nearly full and killed it in 6 or 7 turns.

## 3. Klee

**At her best:** a Bomb on the board that she wants two ways at once. The
contested thing is physical and visible, which no other kit manages as
cleanly.

**What I like.** This is the best kit of the four and I would change little.
The defences are keyed to the same decision as the offence, in opposite
directions (Grounded pays for holding, Run Away! for cashing, a Mine for
both), so choosing cook or cash also chooses how she survives. The lore does
real work: Jean's grounding, the confiscations and the running away are the
survival half of her story and became the survival half of her kit. Sparks
give her a second currency that turns explosions into Block, cards or
Energy, which is why her act-3 game holds together.

**What I do not.**
- **React is a third of her brief and absent from most solo runs.** Three of
  six seats never set off a reaction; Sparkborne Magic and Aftershock went
  unplayed. [USER] ruled to keep it companion-dependent, and I would not
  reopen that. But two Rare slots that most solo decks cannot turn on are
  the most expensive kind of dead offer. When the companion slot comes back,
  this is the first thing it should fix.
- **Sparks never bind.** Four seats ended fights holding 6 to 20, and
  [USER] "never really felt pressed for them". With no cap, Fireworks Finale
  (0 cost, 5 to ALL per Spark) and Spark Knight are the two cards I would
  watch at Balance.
- **The promise's third question has no card.** The brief asks "when, how
  big, and whether you are standing too close". Nothing made her stand too
  close until the status package; Dazed and Confiscated are now that price,
  and I think it is the right one.

**Cards.** Run Away!, Favonius Escort, Alice's Recipe and Boom Badge were
each named NEVER AGAIN once. Alice's Recipe is the one I would look at: a
Rare that only a deck holding Bombs for three turns can use, in a pool whose
winning decks set off every turn.

**Verdict:** ship her to the status-package round as planned. No pick.

## 4. Kokomi

**At her best:** the morning the Plans land, in an order she chose. Opening
Gambit into a damage Plan, or Open the Casket into Sango Isshin, are turns
no base character has.

**What I like.** Playing a card *onto the jellyfish* is a new physical verb,
and it is hers. The order riders make the queue a puzzle. The cards that
read the board at carry-out (Tide Wall, Flank, Evening Watch) are the best
designs in the pool, because they turn the delay into information. The
open-Plan rule is a good ruling for the same reason, and it is the first
change that makes the delay pay in something other than size.

**What I do not.**
1. **She pays a turn and is paid the going rate** (§2.4). The Casket is the
   only wage, it pays once, and seats misread it every round ("opened it at
   2", "dead weight after round 4").
2. **The open-Plan rule helps less than it looks.** It converts a Plan to
   its now-line, but the 2026-09-27 review deliberately removed Block
   now-lines. In the current pool only Kurage's Oath, Tide Wall, Lull, Tidal
   Screen, Sea Glass Harvest and The Moon have one. It is the right rule; it
   is not by itself the fix.
3. **The pool is wide and thin.** Plan volume, the Big Plan, Tide Control,
   Dusk Guard, the status answers and the Casket readers are six sub-decks
   in 78 cards, and two of them reward opposite things. Lull, The Long Game,
   Undertide Lance and Measured Breath pay for *exactly one* or *no* Plan
   waiting, in a pool whose Commons include five 0-cost Plan feeders. The
   sim already has the Big Plan 10 points behind volume. I would drop the
   "alone" conditions and let the Big Plan live on Energy paid (Weight of
   the Plan, Grand Design), which the feeders never add to.
4. **Seven status cards is too many.** Plans resolving after the draw so
   they can clean the next hand is a clever read of rule 2; Tidecleanse and
   Kelp Wall carry it. But the batch took seven slots and cut two of the
   Commander loop's cards (Rally, Chain of Command) to pay for them. Flotsam
   Surge and Riptide Ruin make statuses to feed a sub-theme Klee got the
   same day.
5. **She is the most complex kit and the first to die.** Two-line cards,
   the either/or, Dusk, the queue order, the Casket and now a chooser. The
   complexity budget went to the queue, and the queue only matters once
   three Plans wait.

**Lore.** The strategist is there and it is the right pillar to build on.
The other two are missing, and both are the ones Genshin players know her
for.
- **The healer.** Her jellyfish is the best-known healing summon in the
  game. Here the Bake-Kurage is a mailbox: it never acts unless told and it
  never heals. The 2026-09-27 review ruled healing back "through her relics
  and potions" (pick 3a); that set is still unbuilt and she still borrows
  the Silent's Poison and Shiv relics. `LAW.md` exempts "potions and
  relic-scale trickles", so the Burning Blood shape is open to her.
- **The Hydro support.** "Hydro auras never mattered in six fights." The
  same review ruled "plan the reaction" as her first growth batch (pick
  2a); the pool reached 78 without it. Varka's best turns are all reactions,
  and a planned companion hit landing on a wet enemy is the burst her deck
  lacks.
- **One I would add: she is the consistency character.** Her Genshin passive
  trades all crit for steady healing: no spikes, no bad turns. Today she is
  the opposite, and her deaths are all "no answer in hand". A Block Plan
  written yesterday is exactly an answer that does not need to be in hand
  (§2.2). I would lean the pool into that: **Plans as insurance**, with Tide
  Wall's shape (Block sized to the intent, read at carry-out) reaching
  Common at a smaller number. For example Bubble Ward as "Plan: Gain 4
  Block, and 4 more if an enemy intends to attack."

**What I would do, in order** (re-ordered after §2.8).
1. **Make the Casket pay more than once (pick 1).** It is the only thing
   in her kit that scales, the records show it dead in exactly the fights
   she loses, and the delay paper already names it as the next variable.
2. **The opening Plan (pick 2), after that round.** "Kokomi wins the fight
   before it starts"
   is the brief's first sentence; make it literal. The Bake-Kurage starts
   each combat with a Plan already written. With the open-Plan rule that is
   a choice of 6 Block or 7 to ALL on turn one, made with the first intent
   showing, so every fight opens on a Plan decision instead of a hand of
   basics (which also answers R268's "Plan-less hand"). It needs no number
   moved on any card.
3. **The jellyfish heals after the fight (pick 3).** Small, relic-scale,
   tied to Plans carried out. It is her identity and the law allows it.
   The records do not make it urgent (§2.8), so it can wait for her own
   relic set.
4. **Freeze the pool at 78** until two rounds clear act 1. Within it, swap
   rather than add: the "alone" conditions off (point 3), one or two status
   cards back out for "plan the reaction".
5. **Make the open-Plan chooser opt-in.** One flip in about 57 screens
   (§2.8) is a click a turn for nothing. Carry out the Plan lines unless
   the player taps a waiting Plan to flip it; the rule stays, the screen
   goes.
6. **Plan the reaction.** The one seat that cleared two acts did it by
   freezing enemies with a Cryo companion on her Hydro. That batch was
   ruled on 2026-09-27 and never built; it is the first card work I would
   do once the Casket is read.

## 5. Furina

**At her best:** a Spend choice on every card, priced in the same bar that
is keeping her alive. "Stripping 32 Block to cancel a 23-damage attack"
from the forecast is the best single play in any record I read.

**What I like.** This is the most original kit. A performer is a shield, a
bank and a body at once, and Spend makes the player choose which it is this
turn. The Guest Stars as Defect's orbs with jobs is a strong frame, and
"Stars tax Fanfare, Supports make it" is a real draft tension. The Solo
cards are the best lore in the project: the 500-year one-woman show as a
deck that fires the cast and plays alone.

**What I do not.**
1. **The rulebook is the heaviest of the four.** Twelve rules, and most of
   them carry exceptions (the full-stage summon, Wriothesley, who summons on
   an empty stage, Bows inside a hit, back-first Spends). Every round has
   found a silent failure in them. I would treat "one fewer exception" as a
   goal of every future pass.
2. **Her defence cannot grow** (§2.3). The front bar is her only off-hand
   defence, and the last two passes both shrank it (the fade now takes the
   front; the +1 regain is gone). The pool round already flags this for
   [USER]'s next run; I agree it is the thing to watch.
3. **Of her seven Spend-mode cards, five deal damage, one draws and one
   blocks.** Interposition is the only card that turns Fanfare into Block at
   a Spend rate. If Spend is where her power lives, her defence should live
   there too.
4. **Pneuma is not a mode.** Ousia was chosen 6 of 7 times, because Pneuma
   doubles Block from acts and only Usher's act gives any.

**Lore.** Mostly excellent. One miss with a mechanical use: in Genshin,
Fanfare rises when HP *changes*, in either direction. The crowd loves the
drama. Here only her co-op card does that (The Crowd Roars). A solo version
("Whenever you lose HP, your front performer gains 2 Fanfare") is true to
the source and is off-hand defence that arrives exactly when it is needed.

**What I would do** (after [USER]'s run on the rules pass, which the pool
round already says comes first; no pick, these follow from his ruling):
- **Defensive Spends, on the cards the seats named weak.** Regal Bearing
  and Commanding Gaze keep their weak plain modes and gain a Spend mode
  (for example Regal Bearing: "Spend 3: gain 12 Block and apply 2 Weak
  instead"). This is "Block cards weak, Spend cards strong" applied to
  defence.
- **Block when a performer Bows**, as an Uncommon Power. Spends cause Bows,
  so her damage engine makes Block as a by-product; and a Bow caused by a
  hit pays inside that hit (rule 7), which is the first answer in her pool
  to a multi-hit.
- **Pneuma: each act also gives 2 Block.** Then it scales with the cast,
  with Bis!, Tutti! and Full House, and the Rare has two real modes.
- Final Bow ("the dud") is where I would find the slot.

## 6. Varka

**At his best:** an applier, then the Anemo card, then Four Winds'
Ascension last. Reaction ordering is the best turn-by-turn puzzle in the
project, and it is the only kit where the element system is the game rather
than a garnish.

**What I like.** "One element at a time" is faithful to his Genshin kit and
makes the draft a question. The random starter Knight gives each run a
different opening. Knights as his personal companions is the right use of
the roster's 4-stars. Four Winds' Ascension living outside the deck, like
the Regent's blade, gives the Oath a home from fight one.

**What I do not.**
1. **The bookkeeping.** Four Oath counts, a current element, fresh and spent
   auras, a Swirl payout that depends on the element, and an element that
   moves whenever any card of his applies one. "I only noticed when Azure
   Devour printed 'Deals 1 damage'." Unwavering Banner is a Power that
   exists to switch a rule off, which is usually a sign the rule costs too
   much.
2. **Oath is flat early and runaway late.** It starts at 0 every fight and
   only climbs, and the readers are uncapped and linear. So his first three
   turns in act 3 are as weak as in act 1, and by Oath 35 "everything else
   is filler" (Tidal Bulwark+ gave 60 to 129 Block,
   `varka-expansion-round-2026-10-01.md`). Defence has this worst: the
   readers a split deck can use run at half rate (Gale Mantle at 40 total
   Oath gives 25), the one in Hydro at full rate.
3. **One card carries each run** (Four Winds'+, or Violet Storm+). The
   baseline record is right that the base game does this too; I would still
   watch Violet Storm+, since 11 per discarded card for 1 Energy needs no
   Oath at all.

**Lore.** The wolf is well covered (the Fang, Wolfpack, Andrius's Howl).
The man is not: Varka is loud, generous and hard to hurt, and nothing in
the pool sounds like him. His defence has a ready voice in "laughs it off"
(a cleanse, or Block for debuffs on him), which would also give the kit a
second answer to Weak and Frail beside Barbara's Wellspring Hymn.

**What I would do.** *Withdrawn after §2.8: at the Oath his seats
actually reach in act 3 (5 to 8), the guard mode below is about 7 Block.
His act-3 results are in the base game's range, and I would hold him for
data, as the audit says. The second bullet still stands.*

The round record already owes "a defensive cash-out
that scales the way his Oath damage does". My candidate for that paper was:

- **Give Four Winds' Ascension a guard mode.** "Deal 6 damage, then 3 for
  each Oath of your current element. Or: gain Block equal to your total
  Oath." It is the one card every Varka deck has from the first Oath, and
  it scales as his damage does. Reading *total* Oath is the point: the
  split, Gale and Muster decks are the ones short of Block, and a
  current-element reader would help them least. It also makes the card a
  decision each time it comes round, which the "one-card plan" complaint
  asks for, and it cannot become a wall because it arrives once a deck
  cycle. The rate is for the sim; half the total may be right.
- **Do not add more Block cards.** Three went in on 2026-10-01 and the
  default drafter's act-3 elite read moved from 0.55 to 0.60 against a bar
  of 0.72. Hydro mono at 1.49, with boss stalls rising, says the next Oath
  reader makes Hydro a wall before it makes a split deck safe.

No pick from me; this goes to the defence paper as an option.

## 7. The probes

All on the tier-0 engine with the current kits, full HP unless said, stock
pilots (`ironclad`, `silent`, `demolition`, `salon`; the Kokomi and Varka
expansion sims' own pilot wrappers). Scripts are in this session's
scratchpad, not the repo; each is a few lines over `combat.run_fight` and
`tools/kokomi_expansion_sim.py`'s `fight`, `_offer` and `_draft`.

- **A. Starters** against every act-1 encounter, 150 seeds each.
- **B. Starter plus nine random picks** (offers at 60 / 37 / 3, one of three
  taken at random), 60 decks each.
- **C. Kokomi's 78 against its 40 pre-expansion survivors**, default
  drafter, 120 decks.
- **D. Rule emulations**, 100 decks. The opening Plan is two lines in the
  pilot wrapper's first call: `kokomi_plan.schedule(state, <Kurage's Oath>)`
  then `kokomi_plan.resolve_all(state)`. It is a fixed 7 to ALL; the sim's
  pilot does not use the chooser.
- **E. The stylised act 1** of the expansion sim (N N N N E R N N E R B,
  Casket only), 400 seeds, with D's opening Plan and a heal after each won
  fight.

Caveats: the stock pilot writes a Plan mostly on turns no enemy attacks and
never plays several of her cards (§2.6), so absolute rates are low and only
the differences mean anything. The sim's Ironclad and Silent are starters,
not pools.

## 8. Process, and the logs I would like

- **Two seats cannot tell 30% from 60%, and win or loss is the bluntest
  number a run gives.** HP at each boss door and the hand on the death turn
  are far more sensitive, and both are already in the transcripts.
- **Same seeds for kits and control.** Recent rounds used game-rolled
  seeds, so a kit's round and the base baseline met different bosses. The
  feed round set its seeds (`KK4FEED0929`), so this is free.
- **The logs arrived (§2.8), and the save-file table is the instrument.**
  One row a floor with turns, HP, damage taken and cards offered against
  taken answered in minutes what four seat records had argued about. I
  would attach it to every round record. Two gaps to close: Oath (and the
  Casket's count) by turn, and upgrade marks on the deck lists.

## Picks

**Ruled 2026-10-01.** [USER], on all four picks and the coordinator's
added pick 5 (the open-Plan chooser made opt-in): "On your new picks agree
all around - I think that if it's repeatable, it should probably cost
energy, though, to make this a real choice and not just button mashing
when it comes up?" So: 1a with Open the Casket costing 1 Energy (it was 0);
2a hold; 3a on her own Common relic; 4a fixed seeds with an Ironclad
control and the save-file table; 5a Plans carry out on their Plan line and
a click on a waiting Plan flips it. What the Tokoyo Returns, which fetched
the Casket from the Exhaust Pile, now fetches it from the draw or discard
pile.

Re-ordered after §2.8. Pick 1 is new; the old picks 1 and 2 are now 2 and
3 with their defaults moved to "wait".

1. **Kokomi: the Casket pays more than once.** Her relic, so yours. The
   records show its count dead at 10 to 13 in the boss fights she loses.
   - **(a, default)** Open the Casket loses Exhaust and keeps Retain. Played,
     it goes to the discard pile and comes back with the deck, as Four
     Winds' Ascension does. It is the reading seats already give the card
     ("reads as reusable", `kokomi-feed-round-2026-09-29.md`). Total
     Strength is still one per Plan carried out, which you set and said
     could come down; that number is the knob if act 3 runs away.
   - (b) It keeps Exhaust and returns to hand when the count next reaches 5.
   - (c) Leave it until your own run on the open-Plan build.
2. **Kokomi: the Bake-Kurage starts each combat with a Plan written.**
   A kit rule (it can live on the jellyfish's tip; the Casket's text is at
   the 120-character ceiling already).
   - **(a, default)** Hold it until pick 1's round is read: one variable at a
     time, and the records say hallways are not where she loses.
   - (b) Build it now: a free copy of her Kurage's Oath, upgraded if hers
     is.
   - (c) Drop it.
3. **Kokomi: the Bake-Kurage heals her after combat** (a relic-scale
   trickle, which `LAW.md` exempts; the direction was ruled 2026-09-27,
   pick 3a).
   - **(a, default)** On the Common relic of her own set, when that set is
     built.
   - (b) On the starting relic now, 1 HP per Plan carried out, up to 6.
   - (c) No heal.
4. **Seat rounds: what a round records.**
   - **(a, default)** Still two seats, on two fixed seeds that one Ironclad
     control also plays once; every record carries the save-file table
     (§8).
   - (b) The same, with four seats for a kit that changed a rule.
   - (c) Leave rounds as they are.
