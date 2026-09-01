# Ironclad — the same brief, written for a canon character

**Written 2026-09-01 on branch `kit-overhaul-2026-09-01`. Paper only, and a
calibration exercise, not a design.** The question it answers: can the brief
format used for Klee (`klee-brief-2026-09-01.md`) actually articulate why a
character everyone agrees is fun *is* fun? If it can, the Klee draft can be
held to the same statements. If it cannot, the format is the problem, not
Klee.

The card facts below are the base game's Slay the Spire 2 Ironclad as
extracted into `game_ref/` (90 cards, of which 76 are translated into the
sim's card language; `ironclad_pool.yaml`, `ironclad_char_facts.yaml`). Where I
name a card I use its extracted shape. Nothing here proposes changing him.

---

## 0. The test

1. **Three boards** where the right play is a different verb. (§10)
2. **One contested thing** wanted two ways at once. (§4)
3. **Fight one** puts the tension on the table with nothing hidden. (§8)

## 1. The promise

You are a soldier with a cursed blade and a body that heals overnight. You
hit hard, you bleed on purpose, and you burn your own deck for fuel. Every
fight is a question of how much of yourself you are willing to spend to end
it faster.

In play: the biggest single hits in the game arrive by turn three, the numbers
on his attacks get visibly larger as the fight goes on, and his best defensive
turns are also the turns his deck gets smaller.

What it is not: a wall. He can build one, but the wall is a set-up for a
punch.

## 2. The three verbs

- **Hit.** Attacks that scale with Strength and Vulnerable. Multi-hit cards
  make Strength count twice and three times.
- **Bleed.** Pay HP for energy, Block, draw or damage. The relic gives some of
  it back at the end of a won fight, so bleeding is a bet on winning.
- **Burn.** Exhaust cards, his own included, for Block, draw, energy or damage.
  Every card is also fuel, and the deck that burns gets faster.

Block-as-a-weapon (Body Slam, Barricade) is a fourth verb that only some
decks unlock. It is cards, not a base rule.

## 3. The rules of the kit

1. **HP 80.** The most of any character.
2. **Burning Blood.** Heal 6 at the end of every won fight. This is the only
   rule that is not a card, and the whole Bleed verb rests on it.
3. **Strength** is the shared scaling stat. Every Attack reads it, multi-hits
   read it per hit.
4. **Vulnerable** is the shared setup debuff. The starter has one card that
   applies it and five that cash it.
5. **Exhaust** is a shared mechanic with shared payoffs. Nothing about it is
   Ironclad-only, which is why Burn feels like discovering a rule rather than
   being told one.

Five rules, and three of them are the base game's, not his. That is the
"simple cards in wide shared systems" observation from the 08-26 brief,
stated as a design fact: **most of what makes Ironclad's verbs pay off is not
printed on Ironclad's cards.**

## 4. The contested thing

**HP is both his life and his fuel, and the relic refills a little of it each
fight.** Bloodletting turns 3 HP into 2 energy; Blood Wall turns 2 HP into 16
Block; Offering turns 6 HP into 2 energy and 3 cards; Hemokinesis turns 2 HP
into 15 damage. Each one is a good deal in a fight he wins fast and a bad deal
in a fight he does not, and Burning Blood's 6 is the interest rate. He also
reads the bleeding: Spite and Rupture pay him for having lost HP this turn.

The second contest is the card itself. A Strike in hand is 6 damage or, to
True Grit, Second Wind and Fiend Fire, it is 5 Block, 5 Block, or 7 damage
plus a smaller deck. Burn decks are constantly asking which card is worth
more gone than played.

## 5. The three loops

### 5.1 Strength — "the numbers get big"

Inflame, Demon Form, Setup Strike, Fight Me, Rampage, then multi-hit cashers:
Twin Strike, Sword Boomerang, Whirlwind, Conflagration.

- **A turn looks like:** a Power on turn one or two, then every Attack is
  bigger than it was, and the Whirlwind turn hits four times per enemy.
- **The payoff moment:** Strength 9, Whirlwind for three, three enemies each
  take 42.
- **The decision:** take the Power turn now and eat a hit, or hit now and
  scale later. Against a spike enemy the answer flips.
- **Weakness:** the fight that ends before the scaling matters, and the boss
  with Artifact.

### 5.2 Burn — "the deck becomes a machine"

True Grit, Burning Pact, Second Wind, Fiend Fire, Ashen Strike, Evil Eye,
Forgotten Ritual, Drum of Battle, with Feel No Pain, Dark Embrace and
Corruption as the engines.

- **A turn looks like:** exhaust three cards, gain 9 Block from Feel No Pain,
  draw three from Dark Embrace, and end the turn with a smaller, better deck
  and full energy from Forgotten Ritual.
- **The payoff moment:** the turn the deck is eight cards and every one of
  them is a keeper, and Fiend Fire empties the hand for 35.
- **The decision:** which card to burn. The Strike you might need next turn,
  or the Defend you need now.
- **Weakness:** it is slow to assemble, and a fight that ends on turn two
  never rewards it. The Rare engines are Rare.

### 5.3 Wall — "Block is a weapon"

Barricade, Juggernaut, Colossus, Stone Armor, Flame Barrier, Impervious,
Unmovable, with Body Slam as the cashout.

- **A turn looks like:** Block, Block, Block, and the number in the shield
  icon becomes the number on Body Slam.
- **The payoff moment:** Barricade on turn two, 48 Block on turn five, Body
  Slam for 48 at one energy.
- **The decision:** every Block card is now also an Attack, so the question
  "do I need Block this turn" becomes "do I want the Slam bigger."
- **Weakness:** a single Rare gates it, and until Barricade lands Block is
  just Block.

### 5.4 Bridges

Bash in the starter bridges Hit and everything: Vulnerable makes the Strength
number and the Slam number bigger. Blood Wall and Breakthrough bridge Bleed
and Wall or Hit. Second Wind bridges Burn and Wall. Every loop's cheap cards
are the other loops' fuel.

## 6. The intended weakness

**He cannot draw and he cannot go wide.** Card draw is Pommel Strike, Battle
Trance and Offering. AoE is Breakthrough, Thunderclap, Whirlwind and Stomp.
Against three enemies with a Strength-less deck he kills one per turn and
takes hits from the other two. The weakness is felt in every act-2 hallway,
and it is what makes Whirlwind and Sword Boomerang feel like finding water.

## 7. What is *not* in the kit, on purpose

No card-generation engine, no discard synergy, no orbs, no stances, no
persistent minions. Everything he does is visible as a number on a card, a
number on his Strength icon, or a number in his HP bar.

## 8. What fight one teaches

Starter: Strike ×5, Defend ×4, Bash. Relic: Burning Blood.

Turn one the player sees Bash (8 and Vulnerable 2) and five Strikes. The
lesson is a two-card combo: Bash first, then Strike for 9 instead of 6.
Setup, then payoff, from fight one. Burning Blood teaches the second lesson
without a card: you healed 6 at the end, so the HP you lost was not all lost.
Bleed becomes affordable before the player has seen a single Bleed card.

## 9. Failure modes he avoids

- **The delayed Strike:** none. Every attack lands now.
- **The second energy pool:** none. Energy comes from HP or from exhausting,
  both visibly priced.
- **Auto-fire:** none. Demon Form is the only thing that happens by itself,
  and it happens to the player's own Strength icon.
- **Watch it rise:** Strength rises because the player played a Power; Block
  rises because the player played Block. Nothing accrues from nothing.
- **Word salad:** the Commons are one line. Twin Strike is "5 damage twice."

## 10. The three-board test (turn five)

**Board A, Strength.** Three Ruby Raiders at 12, 14 and 20. Strength 5 from
Inflame and Setup Strike. Hand: Whirlwind, Twin Strike, Defend, Strike, Bash.
Energy 3. Right play: Whirlwind for 3: three hits of 10 to each enemy. All
three die. **Verb: Hit, wide.**

**Board B, Burn.** Act-1 boss at 60, intent 20. Feel No Pain and Dark Embrace
in play. Hand: Second Wind, Strike, Strike, Defend, True Grit. Right play:
Second Wind exhausts Defend and True Grit for 10 Block plus 6 from Feel No
Pain, draws two from Dark Embrace, then the two Strikes. Block 16, draw 2,
deck two cards smaller, 12 damage. **Verb: Burn, for defence and draw.**

**Board C, Wall.** Same boss at 60, intent 20. Barricade in play, Block 34
carried from last turn. Hand: Body Slam, Defend, Defend, Iron Wave, Strike.
Right play: Defend, Defend, Iron Wave for 15 more Block, then Body Slam for
49. Boss to 11 and the Block is still there. **Verb: Block, as an attack.**

Three boards, three different things done with the same energy.

## 11. Turn scripts

### Script A — fight one, Ruby Raiders, starter deck

**Turn 1.** Hand: Strike, Strike, Bash, Defend, Defend. Incoming: Axe 5,
Brute 7. Bash the Brute (8, Vulnerable 2), Strike the Brute (9). Brute 32 to
15. Take 12. The player learned the combo and paid 12 HP for it, and the
relic will give 6 back.

**Turn 3.** Brute dead, Axe at 9 with Big Swing 12 coming, Crossbow at 19
reloading. Hand: Strike ×3, Defend, Bash. Bash the Axe, Strike it, dead. One
Strike into the Crossbow through its 3 Block. Take 0. Every card was a hit.

**Turn 5.** Crossbow at 10, Fire 14 coming. Strike, Strike, dead. Fight over on
turn five, 68 HP, plus 6. The lesson: he wins by hitting, he loses HP doing
it, and the relic makes that sustainable if the fights are short. Nothing was
hidden and no keyword was needed.

### Script B — act-1 boss, Burn deck

Deck adds since fight one: True Grit, Burning Pact, Feel No Pain, Second Wind,
Shrug It Off, Armaments.

**Turn 1.** Hand: Feel No Pain, True Grit, Strike, Strike, Defend. Incoming 12.
Feel No Pain (1). True Grit (1): 7 Block, exhaust a Strike, 3 more Block from
Feel No Pain. Defend. 15 Block, take 0, one fewer Strike forever. The player
chose to make the deck smaller on turn one.

**Turn 3.** Hand: Burning Pact, Second Wind, Strike, Bash, Defend. Incoming 20.
Burning Pact exhausts Defend, draws 2, +3 Block. Second Wind exhausts the two
drawn Skills: 10 Block plus 6. Bash. Block 19, one damage card played, deck
three cards smaller. **Quiet, defensive, and the deck is now mostly Attacks.**

**Turn 6.** Deck is 9 cards. Hand: Strike, Strike, Bash, Shrug It Off,
Armaments. Every draw is live. Bash, Strike, Strike for 26. The machine is
assembled and the turns are loud again. The script shows what Burn promised:
the middle turns are about the deck, the late turns are about the damage.

### Script C — act-1 elite, Strength deck

Deck adds: Inflame, Twin Strike, Sword Boomerang, Whirlwind, Setup Strike,
Shrug It Off.

**Turn 1.** Hand: Inflame, Twin Strike, Strike, Defend, Defend. Incoming 11.
Inflame (Strength 2), Twin Strike for 8 twice, take 11 with 5 Block. The
Power turn cost 6 HP.

**Turn 3.** Strength 4 after Setup Strike. Hand: Sword Boomerang, Whirlwind,
Strike, Defend, Bash. Whirlwind X=2: two hits of 9. Sword Boomerang: three
hits of 7. 39 damage from two cards. **The number on every card is bigger
than the card says.**

**Turn 6.** The elite is dead on turn five. The script ends early, which is the
Strength loop's promise: it does not defend, it ends fights.

## 12. What the format captured, and what it did not

**Captured.** Every sentence in §4 to §6 is checkable against the card list
and says something a player would recognise from play: HP as fuel with an
interest rate, the card as fuel, the numbers getting bigger, the deck getting
smaller, the wall becoming a punch, the missing draw. The three-board test
separates the loops cleanly. The turn scripts read like turns.

**Not captured, and worth naming.**

1. **Most of his fun is borrowed from shared systems.** Strength, Vulnerable
   and Exhaust are the base game's, and their payoffs live on relics,
   potions and other cards he did not print. A brief for a *mod* character
   cannot borrow that way unless the mod's shared layer is as wide. That is
   the one structural disadvantage every Teyvat character has, and the brief
   format does not make it visible on its own. The Klee draft leans on
   Bombs, Sparks and Pyro, all three of which are private systems.
2. **Rares change a rule, not a number.** Barricade, Corruption, Dark Embrace,
   Juggernaut and Feed each rewrite one sentence of how the game works for
   him. The format has no line for "which rule does this loop's Rare break."
   It should.
3. **The weakness is felt through the map, not the fight.** "Cannot draw,
   cannot go wide" is a statement about act-2 hallways and about the draft
   screen, where Whirlwind is a relief. The Klee draft states its weakness as
   a combat fact only.
4. **The relic makes a whole verb affordable before its cards appear.**
   Burning Blood is the reason self-damage reads as a deal rather than a
   cost. The format asks what the relic *teaches*; it should also ask what it
   *pays for.*
5. **The verbs cross currencies in every direction.** HP becomes energy,
   cards, Block and damage; cards become Block, draw, energy and damage;
   Block becomes damage. The Klee draft crosses bombs into damage, Sparks and
   Block, and Sparks into attacks and skills. Fewer directions, and none of
   them reach cards or energy.

These five are the revisions to make to the Klee brief. The format holds;
its lines were incomplete.
