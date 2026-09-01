# Klee — character brief, draft 2

**Written 2026-09-01 on branch `kit-overhaul-2026-09-01`. Paper only.** No sheet,
no code, no register row, no stamp moves. This is the D1 brief the charter asks
for and the shipped kit never had: the player promise, the verbs, the tension,
the three loops, the weakness, and what fight one teaches. It is written to be
read in fifteen minutes and argued with.

Draft 1 was written before the same exercise was done for a canon character
(`ironclad-brief-calibration-2026-09-01.md`). Draft 2 is revised against that
calibration. §14 lists exactly what changed and why; `git diff` on this file
shows the words.

---

## 0. The test this brief has to pass

Before any card is authored, three questions, answered in this document:

1. **Three boards.** Can I describe three different turn-five board states
   where the right play is a different verb? (§10)
2. **One contested thing.** Is there one resource the player wants for two
   different reasons at once, with a real cost either way? (§4)
3. **Fight one.** Does the starter deck put that tension on the table on turn
   one of fight one, with nothing hidden? (§8, §11 script A)
4. **Borrowed systems.** Which of her payoffs live in the mod's shared layer
   rather than on her own cards? (§3 rule 5, §5.5)
5. **The rule each Rare breaks.** Does each loop have a Rare that rewrites one
   sentence of how she works, not just a bigger number? (§5)
6. **What the relic pays for.** Which verb is affordable only because the
   relic exists? (§8)

If any answer is no, the kit is one-dimensional and no amount of card
authoring fixes it. Questions 4 to 6 were added by the calibration.

---

## 1. The promise

You are a small child with a bag of explosives and no supervision. Everything
you touch is going to blow up. The only questions are **when**, **how big**,
and **whether you are standing too close.**

In play: Klee produces the largest single-turn explosions in the game, and she
sets every one of them up herself. A bomb is damage she has already paid for
and not yet collected. She decides when to collect it, and the game keeps
giving her reasons to collect early and reasons to wait.

What it is not: a second energy pool, a poison clone, or an attack deck with a
delay on it.

## 2. The three verbs

- **Plant.** Put a Bomb on an enemy. A Bomb is a number sitting on that enemy,
  visible to everyone.
- **Cook.** Leave it there. Every Bomb grows at the start of her turn. Cooking
  is a verb because her attacks are what cash it, so *not attacking that enemy*
  is a decision she makes on purpose.
- **Set off.** Hit the enemy with an Attack. Every Bomb on it goes off at its
  current size. Setting off is where Sparks come from and where the big payoff
  cards read.

Chain reactions, moving bombs, and reacting bombs are cards, not base rules.

## 3. The rules of the kit

Six sentences. If a rule is not here, it is a card.

1. **Bomb.** A numbered charge on an enemy. At the start of Klee's turn every
   Bomb grows by **2** (placeholder). A Bomb never goes off on its own.
2. **Set off.** When any Attack card Klee plays hits an enemy, a companion's
   Attack included, every Bomb on that enemy goes off, dealing its number as
   Pyro damage. **The explosions resolve before the Attack's own damage.** (So
   the cooked number is the one that reacts, and a killing blow from the
   Attack does not waste the bomb.)
3. **Jump.** If an enemy dies with Bombs on it, they jump to a random enemy at
   their current size. Overkill is redistributed, not wasted.
4. **Spark.** Each Bomb that goes off gives Klee 1 Spark. Sparks are her second
   currency: some cards cost Sparks instead of energy, printed as a cost badge.
   No cap. Sparks are lost at the end of combat.
5. **Pyro.** Every Klee Attack applies Pyro, and so does every explosion. An
   explosion is an ordinary Pyro hit: every shared rule that touches a hit
   touches it, so Vulnerable and Weak on the enemy, Strength on Klee, and
   every reaction in the element table apply to a cooked bomb without a word
   printed on her cards. She enables any reaction and triggers none alone.
   Off-element auras come from companions, as the law says now.
6. **Nothing fires by itself.** No start-of-turn detonation, no automatic free
   attack, no "at 3 Sparks". Every explosion is her card, her Attack, or her
   Rare.

Persistent UI: the Bomb badge on the enemy showing its current size, and the
Spark count. That is the whole rules display.

## 4. The contested thing

**The Bomb on the board is the thing she wants two ways at once. A bomb is
both her shield and her damage, and she can only have one of them at a time.**

- While it sits, it grows, and her best defensive cards read it (Block per
  Bomb on the board). Cooking is safer than it looks, as long as she keeps
  bombs on the board.
- When she cashes it, the damage lands, the Sparks arrive, and the Block engine
  goes with it. Cashing is the moment she is most exposed.

Every Attack she plays is therefore also a targeting decision about *which
bombs to collect*. Attack the bombed enemy and she collects now. Attack the
other enemy, or play Skills, and she cooks. The enemy's intent tells her which
one she can afford this turn. This is the Defect's hold-or-evoke question with
the orb sitting on the enemy instead of beside her, and the answer is different
in every fight.

Sparks are the second, smaller contest. A Spark buys either a free Attack now,
which cashes more bombs and mints more Sparks (tempo), or a Spark-priced Skill
that plants, grows, or blocks (setup). Generation comes only from explosions,
so she cannot bank Sparks without collecting bombs. Lean in and it flows;
otherwise it is stingy, which is the Regent's Stars governor by scarcity and
not by cap.

## 5. The three loops

Each loop is a different shape of turn, not a different number.

### 5.1 Cook — "the big one"

Few bombs, grown large, cashed with one heavy Attack. The boss plan.

- **A turn looks like:** plant on turn one, then two or three turns of Block
  that scales with bombs on the board and Skills that grow them, then one cash
  turn with a multiplier.
- **You draft:** Hide and Seek (Block per Bomb), Chain Fuse and Explosives
  Workshop (grow faster), Careful Arrangement (pile every Bomb onto one
  enemy), Big Badda Boom and The Big One (cash multipliers), Remote Detonator
  (cash without an Attack).
- **The payoff moment:** a single 30-plus explosion, then the Sparks it minted
  pay for the follow-up.
- **The decision every turn:** "is it big enough, or can I afford one more
  turn?" The enemy's intent answers it.
- **The Rare that breaks a rule:** Slow Fuse (Power): her Attacks no longer
  set off Bombs; only her Skills and Quick Fuse do. Rule 2 is gone, and she
  can hit the bombed enemy every turn while it cooks. Barricade's job.
- **Weakness:** hallways with three small enemies, and anything that hits
  harder than her Block can grow.

### 5.2 Spray — "everything explodes now"

Many cheap bombs, cashed immediately by Spark-priced Attacks, which mint the
Sparks for the next one. The hallway plan and the Shiv analogue.

- **A turn looks like:** six to nine card plays, random targets, bombs going
  off on every enemy, the board cleared by turn two or three.
- **You draft:** Pop! and Mine Toss (cheap bombs), Fwoosh! and Tinder Toss and
  Bang Bang! (Spark Attacks), Rapid Fire (four random hits cash the whole
  board), Chained Reactions (every explosion plants a new Bomb somewhere),
  Sparks 'n' Splash (end of turn, set off a random enemy).
- **The payoff moment:** the chain, when one Attack sets off three enemies'
  bombs, the Sparks pay for two more Attacks, and the turn does not end.
- **The decision every turn:** where to send the random hits to keep the chain
  alive, and when to stop cashing and leave one bomb cooking for the Block.
- **The Rare that breaks a rule:** Sparks 'n' Splash (Power): at the end of
  her turn, set off a random enemy's Bombs. Rule 6 is gone; something now
  fires by itself, and the Spray deck stops needing an Attack in hand to keep
  the chain alive.
- **Weakness:** one big enemy with Block, and running out of bombs, which means
  running out of Sparks.

### 5.3 React — "the one that goes off twice"

Klee's explosions are Pyro, so a Bomb that goes off on an enemy carrying a
foreign aura reacts: Vaporize on Hydro, Melt on Cryo, Overload splash on
Electro. The multiplier lands on the cooked number, not the card's number.

- **A turn looks like:** a companion applies Hydro this turn, and next turn she
  cashes the bomb for one and a half times its size. Sequencing is the whole
  game.
- **You draft:** Dahlia, Kaeya, Diona, Fischl from the Mondstadt pool (the
  appliers), Sucrose (Swirl spreads the aura), Sizzle and Perfect Timing and
  Flame Dance (pay extra against an aura), Vermillion Pact (double the
  amplifier).
- **The payoff moment:** a cooked 15 that Vaporizes into 22 and applies Pyro
  on the way out.
- **The decision every turn:** cash now for the plain number, or wait one turn
  for the aura and risk the enemy's swing.
- **The Rare that breaks a rule:** Vermillion Pact (Power): when an explosion
  reacts, the Attack that set it off reacts too. The shared "one aura, consumed
  by the first hit" rule is broken for her chain, so the whole cash turn is
  multiplied and not just the bomb.
- **Weakness:** she cannot apply the second element herself. Without an
  applier in hand this deck is a slightly worse Cook deck, which is fine, and
  it is the archetype that gets better in co-op without needing it.

### 5.4 Bridges

- Jumpy Dumpty (starter): hits, then plants on what it hit. Spray and Cook
  share it.
- Sorry, Jean...: Block plus a bomb on a random enemy. Cook's defence, Spray's
  fuel.
- Quick Fuse: a Spark to set off one enemy without an Attack. Spray's
  economy, Cook's cash button when the hand has no Attack.
- Any Pyro-applying companion play into a cooked bomb. React reaches into both
  other loops rather than needing its own.

### 5.5 Currencies, and which way they cross

Ironclad's verbs turn HP into energy, cards, Block and damage, and cards into
Block, draw, energy and damage. Draft 1 of this brief turned bombs into
damage, Sparks and Block, and Sparks into attacks and Skills, and nothing
reached cards or energy. Draft 2 adds the missing directions and names where
they live:

- **Bombs → damage** (rule 2), **→ Sparks** (rule 4), **→ Block** (Hide and
  Seek, Common).
- **Bombs → cards:** Ammo Scavenging (Common, 1 energy): plant a Bomb 4, then
  draw a card for each Bomb that went off this turn. Cashing now also refills
  the hand, which is Dark Embrace's job for Burn.
- **Sparks → attacks** (Fwoosh! and friends, Common), **→ Block and setup**
  (Dig In, Powder Charge, Uncommon), **→ energy only at Rare:** Sugar Rush
  (Rare, 2 Sparks, exhaust): gain 2 energy and draw 1. Below Rare, Sparks
  never become energy, or they are a second energy pool.
- **Reactions → Sparks:** Catalytic Converter (Uncommon Power): a reacting
  explosion gives 2 Sparks instead of 1. React feeds Spray.

Every currency reaches every other one somewhere in the pool, at the rarity
that keeps it a discovery rather than a default.

## 6. The intended weakness

**She cannot stall.** Her Block is either plain and small, or borrowed from
bombs that she then has to cash. She has little card draw, no scaling Power
that does not run through bombs, and her multi-hit attacks pick their own
targets. Against an enemy that out-damages her Block she must cash early and
small, which is exactly the situation she hates.

The weakness is load-bearing because it is what makes cooking a bet rather
than a free upgrade.

**Where the player feels it.** On the draft screen: every Block card she is
offered is 5 for 1 energy and never scales except through bombs, her draw is
two Commons, and half her Attacks pick their own targets. On the map: an
act-2 hallway with three enemies that each hit for 10 cannot be cooked, so
Spray is the only line and a Spray deck without enough Spark Attacks is a
deck of Pop!s. She feels the missing Block the way Ironclad feels the missing
draw, and the companion pool's plain Block bodies read as relief for the same
reason Whirlwind does for him.

## 7. What is deliberately gone from the shipped kit

| Shipped | Proposed | Why |
|---|---|---|
| Bombs detonate at the start of her next turn | Bombs only go off when she hits the enemy | A bomb that fires itself is a delayed Strike and asks nothing |
| Bombs are a fixed number | Bombs grow every turn they sit | Waiting has to be worth something or cashing is never a choice |
| Sparks from many Common Skills | Sparks only from explosions | Otherwise Sparks are a second energy pool |
| "At 3 Sparks the next Attack is free" | Sparks are an alternative cost on specific cards (kept from the redesign) | Nothing fires by itself |
| Overkill wastes the bomb | Bombs jump to another enemy | Multi-enemy chaos, and Spray stays alive |
| Reaction archetype is co-op-primary and boss-weak by ruling | React is the multiplier on both other loops | It should make the deck you already have better, not need its own deck |

## 8. What fight one teaches

Starter deck, ten cards: Kaboom! ×3 (1 energy: 6 damage), Ka-pow! ×1 (1 Spark:
7 damage), Duck and Cover ×4 (1 energy: 5 Block), Pop! (0 energy: plant a
Bomb 5), Jumpy Dumpty (2 energy: 8 damage to a random enemy twice, then plant
a Bomb 6 on each enemy it hit).

Relic, Pounding Surprise: the Spark rule in §3. It is the only free Spark
source, and it **pays for a whole verb**: every Spark-priced card in the pool
is playable only because explosions mint Sparks. Without the relic, Spray is
a deck of dead cards, which is exactly Burning Blood's relationship to
Ironclad's Bleed. The player meets the relic's job on turn two of fight one,
when the first explosion turns Ka-pow! from a blank into a free 7.

Turn one, fight one, the player sees: a 0-cost card that puts a 5 on an
enemy, three Attacks that would collect it, and a card in hand that costs a
Spark they do not have yet. Every verb is on the table, the badge shows the
bomb growing, and nothing is hidden. Script A below plays it out.

## 9. Failure modes, named

- **The delayed Strike.** A bomb that is just damage with a delay. Prevented by
  growth, Block-per-bomb, and payoffs that read bombs for something other than
  damage.
- **The second energy pool.** Sparks that only ever buy more attacks.
  Prevented by Spark-priced Skills and by generation that only comes from
  explosions.
- **Auto-fire.** Anything that detonates or spends without the player's
  action. The old start-of-turn rule and the old 3-Spark rule are both this.
- **Watch it rise.** Cooking with no reason to cash early. Prevented by the
  enemy's clock and by the Block engine being the same bomb.
- **The companion-locked loop.** React needs companions, and that is allowed,
  but Cook and Spray must each win without a single companion.
- **Word salad.** Commons print at most two lines. The badge and one character
  rule carry the mechanics.

## 10. The three-board test (turn five)

**Board A, Cook.** Act 1 boss at 90 HP, one Bomb on it at 13. Its intent is a
14 hit. Hand: Kaboom!, Duck and Cover ×2, Hide and Seek, Big Badda Boom. Sparks
2. Right play: Hide and Seek (3 Block plus 2 per Bomb on the board) and Duck
and Cover for 10 Block, take 4, cook to 15, and cash next turn with Big Badda
Boom, which reads the Bomb again. **Verb: Cook.**

**Board B, Spray.** Three raiders at 9, 11 and 20 HP, Bombs at 5 on two of
them. Sparks 2. Hand: Ka-pow!, Tinder Toss, Pop!, Kaboom!, Duck and Cover.
Right play: Tinder Toss (1 Spark: 4 to all) sets off both bombs for 5 each,
minting 2 Sparks, Ka-pow! the survivor at 11, Pop! on whatever is left, and
Kaboom! collects it. Two enemies die, three cards were free. **Verb: Set off,
everywhere.**

**Board C, React.** One elite at 60 HP carrying Hydro from Dahlia last turn.
The aura expires at the end of this turn. One Bomb on it at 9. Hand: Kaboom!,
Chain Fuse, Duck and Cover ×2, Sizzle. Right play: Sizzle now (8 plus 6 against
an aura), because the explosion resolves first and Vaporizes 9 into 13, then
the Attack lands on a fresh Pyro aura. Waiting a turn would grow the bomb by 2
and lose 4 from the multiplier. **Verb: Cash now, for the multiplier, even
though cooking was available.**

Three boards, three verbs. The shipped kit gives the same answer on all three:
play the attacks, the bombs go off next turn either way.

## 11. Turn scripts

Real act-1 enemies from the dossiers where they exist. The boss in script A is
a stand-in with placeholder numbers, because the decision is the point and the
numbers are not. Hands are drawn as stated, not cherry-picked to make the play
obvious.

### Script A — fight one, Ruby Raiders (Spray, from the starter)

**Enemies:** Axe Raider 21 HP (Swing 5 and gains 5 Block, Swing, then Big Swing
12). Crossbow Raider 19 HP (Reload for 3 Block, then Fire 14). Brute Raider 32
HP (Beat 7, then Roar for 3 Strength).

**Turn 1.** Hand: Kaboom!, Kaboom!, Duck and Cover, Pop!, Jumpy Dumpty. Energy
3. Incoming: Axe 5, Crossbow 0, Brute 7.

The safe line is Kaboom! twice into the Axe Raider (21 to 9) and Duck and
Cover. The Klee line is Jumpy Dumpty and Pop! and Duck and Cover. Jumpy hits
twice at random, say Brute and Crossbow, then plants a 6 on each; Pop! puts a 5
on the Axe Raider; Duck blocks 5 and she takes 7 from the Brute. Board at end
of turn: bombs 6, 6, 5 across all three enemies, nothing collected yet, Klee at
55. The player has chosen to eat a hit to load the board, and the badges say
what they will be worth next turn.

**Turn 2.** Bombs grow to 8, 8, 7. Hand: Kaboom!, Ka-pow!, Duck and Cover ×2,
Duck and Cover. Incoming: Axe 5, Crossbow 14, Brute Roar.

Kaboom! the Crossbow Raider: the 8 goes off first, then 6 damage, through its 3
Block. It dies (19 minus 11 minus 3 Block, then the Kaboom). Its bomb has
already gone off so nothing jumps. That minted 1 Spark, which pays for Ka-pow!
into the Axe Raider: 8 goes off, then 7, it dies at 21, and its jump rule is
moot. Two Sparks in hand now, no Spark card left, so two Duck and Cover for 10
Block against the Brute's Roar turn. Board: Brute 32 HP with a bomb at 7 that
has not gone off, Sparks 2, Klee 55.

**Turn 3.** Bomb grows to 9. Hand: Kaboom!, Kaboom!, Pop!, Duck and Cover,
Jumpy Dumpty. Incoming: Brute Beat 10 (7 plus Strength).

Cash or cook. Cook: Pop! adds a 5, Duck and Cover, take 5, and next turn the
bombs are 11 and 7 into a Jumpy Dumpty. Cash: Kaboom! sets off the 9, then 6,
Brute to 17, one Spark, then Kaboom! again to 11, Duck and Cover, take 5. The
fight ends turn 4 either way; the cook line ends it with one card instead of
three and keeps two Sparks for the next fight's... nothing, because Sparks do
not carry. So cash. **The lesson of fight one:** Sparks are for spending, bombs
are for timing, and the badge told you everything.

### Script B — act-1 boss, single enemy (Cook, mid-act deck)

**Deck additions since fight one:** Hide and Seek, Chain Fuse, Careful
Arrangement, Big Badda Boom, Mine Toss, one Dahlia (Sacramental Shower).
**Boss (stand-in):** 140 HP, pattern Swing 12, Swing 12, Crush 20 and gains
Block, repeat. Placeholder numbers.

**Turn 1.** Hand: Pop!, Mine Toss, Kaboom!, Duck and Cover, Hide and Seek.
Incoming 12. Pop! and Mine Toss plant 5 and 5 on the boss (0 and 1 energy).
Hide and Seek: 3 Block plus 2 per Bomb on the board, so 7. Duck and Cover for
12 total. Take 0. Board: two bombs at 5 on the boss, Klee untouched, no Sparks,
nothing collected. She has spent the whole turn not attacking, on purpose.

**Turn 3.** Bombs have grown to 9 and 9 (she played Chain Fuse on turn 2, which
added 2 each and planted a third at 4, now 6). Three bombs: 9, 9, 6. Hand:
Careful Arrangement, Kaboom!, Duck and Cover, Big Badda Boom, Jumpy Dumpty.
Incoming: Crush 20. Energy 3.

This is the decision the archetype exists for. Cash now: Big Badda Boom (2
energy) sets off 24, then 16 of its own, then reads the bombs again for another
24. That is 64, boss to 76, three Sparks, but only one energy left for 5 Block
against a 20, so she takes 15. Cook: Careful Arrangement piles the three into
one bomb at 26 (its own rider adds 2), Hide and Seek is not in hand, so Duck
and Cover and take 15 anyway, and next turn the pile is 28 into Big Badda Boom
for 28 plus 16 plus 28. The cook line costs the same 15 HP and pays 72 instead
of 64 a turn later. Klee at 47 either way. She cooks, and the whole turn was
one Skill and one Block card.

**Turn 6.** Boss at 68 after the turn-4 cash. Bombs: one fresh Pop! at 7. Hand:
Kaboom!, Kaboom!, Hide and Seek, Duck and Cover, Dahlia. Incoming Swing 12.
Sparks 4, and the deck has no Spark card, which the player now notices is the
draft hole. Dahlia applies Hydro for 6 damage. Kaboom!: the 7 goes off first
and Vaporizes into 10, applying Pyro, then 6. Boss to 46. Hide and Seek with no
bombs left is 3 Block, so Duck and Cover too, take 4. The player wanted a
Spark Attack this turn and did not have one. **What the script shows:** the
Cook deck's turns are Skill-heavy and quiet, the cash turn is loud, and the
missing piece is visible on the board rather than in a tooltip.

### Script C — two Damp Cultists (React, with two appliers drafted)

**Deck:** starter plus Dahlia, Kaeya (Frostgnaw, Cryo), Sizzle, Perfect Timing,
Hide and Seek. **Enemies:** two Damp Cultists, 30 HP each, spike class
(placeholder pattern: Chant, then Strike 11).

**Turn 1.** Hand: Kaeya, Pop!, Kaboom!, Duck and Cover, Sizzle. Kaeya on
Cultist A: 6 damage and Cryo. Pop! on Cultist A: bomb 5. Now the choice: Sizzle
A now, which sets off the 5, Melts it into 8, then 8 plus 6 for having an aura,
total 22, Cultist A to 2, one Spark. Or Duck and Cover, and next turn the bomb
is 7 and Melts into 12. The aura lasts two of her turns, so waiting is legal.
She cashes now, because Cultist A at 2 HP dies to anything next turn and the
Strike 11 is coming from both of them. The script is honest that React's
"wait a turn" is often wrong on turn one and right on turn three.

**Turn 3.** Cultist A dead on turn two (its jump rule sent a bomb at 4 to
Cultist B). Cultist B 30 HP, bombs 6 and 5 on it (the jumped one and a Pop!).
Hand: Dahlia, Perfect Timing, Kaboom!, Duck and Cover, Hide and Seek. Incoming
Strike 11. Dahlia: 6 and Hydro. Perfect Timing: bombs go off first, 11
Vaporizes into 16, then 8, and Perfect Timing's rider fires because a reaction
happened, so it plays again: another 8, and the fresh Pyro aura means no
second reaction. Cultist B to 0 from 30. Fight over on turn three, and the
whole thing was a sequence: applier, then Attack, with the bomb in between.

**Turn 5** does not exist for this fight, which is the point of the React
loop: it ends fights a turn earlier than Cook and a turn later than Spray, and
it does so by ordering the same cards differently.

## 12. Defaults taken, and the six things that are genuinely yours

Under the ladder I have taken every default below and I will build on it. You
veto on sight; a veto is one line.

**Defaults taken (Claude's):** growth 2 per turn; explosions resolve before
the Attack; one Spark per explosion; Spark cost printed as a badge (the
redesign's choice, kept); starter as in §8; Hide and Seek at Common with the
per-bomb rider; Sparks 'n' Splash becomes a draftable Rare Power once the
shared Burst meter retires, an end-of-turn auto-cash for Spray; every number
in this document is a sim starting point and none is a design pick.

**Yours, numbered, with the default I will build on unless you say otherwise:**

1. **What makes a Bomb go off.** (1) *Only her Attacks and cards; nothing on
   its own* [default]. (2) A fuse: bombs also go off by themselves after three
   turns. (3) Keep start-of-turn auto-detonation.
2. **Volatility.** (1) *None; the enemy's swing is her only risk while
   cooking* [default]. (2) A bombed enemy that hits Klee sets off its own bomb
   early, on her. Chaotic and on-theme, and it makes cooking on an attacking
   enemy a real gamble. I like it and did not take it, because it adds a
   second rule to the six.
3. **Jump on death.** (1) *Bombs jump to a random enemy at full size*
   [default]. (2) They jump and reset to base. (3) They are lost.
4. **The React loop and the law.** (1) *Companion-fed, as the law stands*
   [default]. (2) Give Klee one own-kit off-element source, which is a LAW
   amendment to "reactions are earned, not given".
5. **The scaling cap in LAW.** (1) *Strike "A2 ≤ 4.0, scaling never tops
   frontload"; her identity is the cook-or-cash tension, not a statline* [my
   recommendation, and a LAW amendment, so yours]. (2) Keep it, which caps how
   large a cooked bomb may get and forces a growth ceiling.
6. **Bomb count and growth.** (1) *Each Bomb grows separately, so three small
   bombs on one enemy cook three times as fast as one big one* [default; it
   makes Careful Arrangement and Bombs Away! interesting]. (2) Growth is per
   enemy, not per bomb.

## 13. What this document does not do

It does not author the 75-card sheet, price a single card, or claim a
winrate. It does not touch Kokomi, whose brief is next, or the companion
layer, whose role is decided after both briefs. Nothing here is a ruling; the
six items above are picks and everything else is a default with a veto.

## 14. What the calibration changed (draft 1 → draft 2)

The Ironclad exercise found the format sound and five of its lines missing.
Each became an edit here:

1. **Borrowed systems made explicit** (§3 rule 5, §0 question 4). Ironclad's
   fun is mostly the base game's shared systems paying out on his cards. Klee
   cannot borrow Strength and Exhaust the same way, so draft 2 states that an
   explosion is an ordinary Pyro hit, which lets the mod's own shared layer
   (elements, reactions, Vulnerable, Weak, Strength) pay out on bombs with no
   private text. Rule 2 now also lets a companion's Attack set off bombs.
2. **One rule-breaking Rare per loop** (§5.1 to §5.3, §0 question 5). Slow
   Fuse breaks rule 2, Sparks 'n' Splash breaks rule 6, Vermillion Pact breaks
   the shared one-aura rule for her chain. Draft 1's Rares were bigger
   numbers.
3. **The weakness felt through the draft screen and the map, not only the
   fight** (§6). Draft 1 said "she cannot stall"; draft 2 says where the
   player meets that.
4. **What the relic pays for, not only what it teaches** (§8, §0 question 6).
   Pounding Surprise makes the Spray verb affordable the way Burning Blood
   makes Bleed affordable.
5. **Currencies cross in every direction** (§5.5). Draft 1 never turned bombs
   into cards or Sparks into energy. Draft 2 adds both, at the rarity that
   keeps them discoveries.

What the calibration did not change: the promise, the three verbs, the six
rules, the contested thing, the three loops, the starter, the failure modes,
the three-board test, and the turn scripts all stood. The format's questions
1 to 3 were the right questions; 4 to 6 were missing.
