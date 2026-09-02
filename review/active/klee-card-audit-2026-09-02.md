Status: OPEN (the Klee card audit; D defaults applied; picks at the end)

# Klee card audit: every prototype row's base and upgrade, read by design

2026-09-02, on the upgrade pass (PR #295). You asked for a designer's read
of the Opus upgrade pass, one agent per character. This is Klee's: all 30
`proto_ko_` rows in `docs/prototype-surface.yaml`, base line and upgrade,
against the base game's own conventions. The yardstick is the one the balance
read used (`review/records/balance-read-prototype-2026-09-02.md` sec.1):
Strike 6 and Defend 5 for 1 energy, Bombs grow by 4 a turn
(`KLEE_OVERHAUL_BOMB_GROWTH`), and Ka-pow! cashes any Bomb for 0 energy, so
a plant is credited its growth. Nothing R242 or R243 ruled today is reopened;
the starter's four cards, growth 4, Sparks 'n' Splash, Alice's Recipe, Chain
Fuse 6, Fish-Flavored Bait 4/4, Careful Arrangement 5 and Sorry, Jean... at 0
stand as ruled.

The Opus pass derived every upgrade from one rule
(`tier0/content/upgrades.py`, `prototype_default_delta`): +3 damage, +3
Block, +2 Bomb, +1 grow, +1 power amount, cost 1 less on a 2-cost, else drop
Exhaust, else add a draw. Most of what it produced is right. Fourteen rows
are not, in three ways: the rule's +1 on a grow is an upgrade nobody would
notice (Chain Fuse 6 to 7); the rule reads a power's `amount: 1` as an on/off
switch, so the two Powers whose printed number IS 1 got "Draw 1 card" instead
of 2; and two rows took the rule's blind last clause where a designer has a
real lever (Sugar Rush lost Exhaust, which makes Sparks the second energy bar
the brief forbids; Sorry, Jean... became a cantrip). One row was broken by
construction, not by the upgrade pass: Flame Dance's rider could never fire.

## 1. Rows changed (D defaults, applied and disclosed)

Base numbers are unchanged on every row. "Was" is the upgraded card the
smith handed back before this pass; "now" is what it hands back after.

| Card | Was (upgraded) | Now (upgraded) | Why |
|---|---|---|---|
| Chain Fuse (C, 1) | grows by 7 | grows by 9 | A grow is damage to be; it takes a Strike's +3, not +1. |
| Careful Arrangement (U, 1) | grows by 6 | grows by 8 | Same rule. |
| Quick Fuse (C, 1 Spark) | grows by 4, then Set off | grows by 6, then Set off | Same rule. Face also rewritten: "grows by 3. Set off." (Set off is sentence-initial, `text-conventions.md`). |
| Explosives Workshop (U, 1) | grow by 1 more, plus "Draw 1 card" | grow by 2 more | The 1 is a printed number, not a switch (`ExplosivesWorkshopGrowthPower` stacks it). Demon Form 2 to 3, Evolve 1 to 2. |
| Catalytic Converter (U, 1) | 1 additional Spark, plus "Draw 1 card" | 2 additional Sparks | Same defect, same fix. |
| Grounded (U, 1) | 7 Block | 8 Block | A Block power moves by 2 (Juggernaut 5 to 7, Plated Armor 4 to 6); 7 is invisible. |
| Tinder Toss (C, 1 Spark) | 5 damage twice | 6 damage twice | A two-hit Attack moves each hit by 2 (Twin Strike 5 to 7); +1 per hit is the three-hit idiom (Sword Boomerang). |
| Big Badda Boom (U, 2) | 15 damage | 16 damage | A 2-cost Attack's hit moves by about a third (Carnage 20 to 28, Sever Soul 16 to 22); a third of 12 is 4. The echo is untouched. |
| Mine Toss (C, 1) | Mine 6 on ALL | Mine 7 on ALL | A Bomb that is the whole card moves by 3, the way Jumpy Dumpty's own 8 to 11 does. |
| Powder Charge (U, 1 Spark) | Bomb 8 | Bomb 9 | Same rule. |
| Ammo Scavenging (C, 1) | Bomb 6 | Bomb 7 | Same rule; its draw clause has no number to move. |
| Sugar Rush (R, 2 Sparks) | Exhaust removed | 3 Energy, Exhaust stays | Adrenaline's shape. A repeatable Spark-to-Energy card is the second energy bar the brief's rule 4 forbids; the brief lets Sparks become energy at Rare ONCE. |
| Sorry, Jean... (C, 0) | plus "Draw 1 card" | Retain | The emergency exit is held while you cook, not cycled. |
| Flame Dance (U, 1) | 8 to ALL, rider unchanged | 8 to ALL, rider now reachable | Not an upgrade fix. The row dealt its 5 Pyro damage FIRST, and a Pyro hit consumes any foreign aura (`AuraPower.cs:205`), so "Set off each enemy with a non-Pyro aura" read the board after the card had eaten the aura it needed. Three seats called it a trap; it was. Effects reordered to rule 2's order (explosions before the rest of the card); face: "Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies." |

Two things had to move in the generator for the sheet to say this: the
authored-face walker in `tools/gen_klee_cards.py` (`_authored_face_numbers`)
now prints an `energy` var when an `energy:` delta moves it, and it no longer
steps its cursor past a Spark price the face does not print (on Sugar Rush
the price 2 matched "Gain 2 Energy" and the `+` face kept the literal). Both
are visible in the generated `ProtoKoSugarRush.cs`.

Every change is a row-level `upgrade:` block, so the Prototype rule itself is
untouched and Kokomi's rows are not affected.

## 2. Rows read and left alone

- **Ka-pow!** (0, Retain, Set off + 4, upgrade 7) and **Jumpy Dumpty** (1,
  Bomb 8 and Mine 3 on ALL when it goes off; upgrade 11 and 4): R242, R243.
- **Fish-Flavored Bait** (4 + Bomb 4; upgrade 7 and 6): R243's number; the
  derived split is Iron Wave's shape and reads fine.
- **Pocket Fireworks** (9; upgrade 12): the plain pressure Attack. Right.
- **Alice's Recipe** (2, grow twice; upgrade cost 1): R243; Barricade's lever.
- **Pop!** (0, Bomb 5; upgrade 7): a free card takes Shiv's +2, not +3, or
  Pop!+ is Jumpy Dumpty's 8 for nothing.
- **Bang Bang!** (2 Sparks: Set off, 8, Bomb 4; upgrade 11 and 6): fine. The
  round-3 seats found it dead only before the opening Spark existed.
- **Rapid Fire** (2: 3 to a random enemy 4 times, Set off each; upgrade 4 x
  4): Sword Boomerang's +1 per hit is right on four hits. Worse than Big
  Badda Boom on one enemy, and that is the point; it is the crowd card.
- **Chained Reactions** (R, 1: a Bomb 3 per explosion; upgrade 4): a Rare
  engine that needs explosions. Noxious Fumes' +1.
- **Sparks 'n' Splash** (R, 2; upgrade cost 1): R243's new body.
- **Sizzle** (Set off, 6, +6 on a reaction; upgrade 9) and **Perfect
  Timing** (Set off, 8, replay on a reaction; upgrade 11): both fine, and
  both can satisfy their own condition because the explosion resolves first.
- **Dig In** (1 Spark, 8 Block; upgrade 11) and **Run Away!** (0: 3 Block, +4
  after an explosion; upgrade 6 and 4): fine.
- **The Big One** and **Fwoosh!**: untouched, because each is a redundancy
  rather than a number. Picks 1 and 2.

Two notes with no action. Explosives Workshop's base +1 per Bomb per turn
reads thin beside Inflame (one Bomb over three turns is +3 damage for a card
and an energy); R243 kept it as the stacking +1 against Alice's doubling, and
round six is the read. Sorry, Jean... removes the LARGEST Bomb
(`ProtoBombPower.RemoveLargestForBlockAndGain`) while the face says "one of
your Bombs"; the largest is the pick a player would make, so it is a wording
note for the shipped sheet, not a defect.

## 3. The pool as a whole

**Spark economy.** She opens with 1 and earns 1 per explosion, Mines
included, so a starter fight with Jumpy Dumpty mints 2 to 5. Seven rows cost
Sparks: five at 1 (Fwoosh!, Tinder Toss, Quick Fuse, Powder Charge, Dig In),
two at 2 (Bang Bang!, Sugar Rush). One Spark buys roughly one energy's worth
(Dig In's 8 Block, Fwoosh!'s Set off + 5, Powder Charge's Bomb 6 against
Pop!'s free 5), and that is the design: the price is scarcity, not a cap.
None of the seven reads as a second energy bar; Sugar Rush would have, once
upgraded, and now does not.

**Redundancy.** Explosives Workshop and Alice's Recipe were the same card
until R243. The next two pairs are worse, because one card strictly dominates
the other at the same price and rarity:

- *The Big One* (R, 3: Set off for double, then 10) against *Big Badda Boom*
  (U, 2: Set off, 12, then the damage the Bombs dealt). On a Bomb B they are
  2B + 10 for 3 energy and 2B + 12 for 2. The Uncommon is cheaper and hits
  harder at every B, and its echo repeats even a reaction's multiplier
  (`EB-270`). The Rare cannot be drafted on purpose.
- *Fwoosh!* (C, 1 Spark: Set off and 5 to a random enemy) against *Tinder
  Toss* (C, 1 Spark: Set off and 4 to a random enemy, twice). Alone, Tinder
  Toss is Set off + 8 to Fwoosh!'s Set off + 5; in a crowd it rolls two Set
  offs to Fwoosh!'s one. Both are random, so Fwoosh! has no aim to sell.

**Rares need setup (R243).** Alice's Recipe, Chained Reactions, Sparks 'n'
Splash, The Big One and Sugar Rush all pay only on a board with Bombs or
Sparks already on it. None is "press button, delete act one".

**Grow versus cash.** Every row lands on one side of the bet or pays for
choosing it: Grounded and Alice's for the wait, Run Away! and the Spark
Attacks for the cash, Sorry, Jean... (now held) as the exit, Mines as both.

## 4. Picks

1. **The Big One.** Dominated by Big Badda Boom (section 3). (1) **Default:
   it triples.** "Set off for triple damage. Deal 10 damage." at 3 energy:
   3B + 10, the Red Knight of Stormbearer Mountains the brief names, and it
   needs a cooked Bomb to be anything. On Jumpy Dumpty after two dawns and a
   Chain Fuse (22) it is 76 to Big Badda Boom's 56. Upgrade stays 13. (2)
   Keep double, own hit 10 to 20: 2B + 20 for 3, a Strike's edge over the
   Uncommon and no new rule word. (3) Cut it; the Rare slot waits for
   Vermillion Pact. Any of the three is a C# change in
   `KleeOverhaulLedger` (the doubling flag) and a sheet row, built with the
   round-six build.
2. **Fwoosh!.** Dominated by Tinder Toss. (1) **Default: it aims.** "Set
   off. Deal 6 damage." for 1 Spark, on the enemy you choose: the Spark-priced
   Ka-pow! every seat since round three has asked for ("a huge stack and
   nothing to light it with"), and the aimed-versus-random trade the base
   game prices Strike against Sword Boomerang by. Upgrade 9. (2) Cut it;
   R243 pick 2's "four of the twelve Commons cost Sparks" becomes three. (3)
   Leave both and move Tinder Toss to Uncommon beside Bang Bang!.

Everything in section 1 is applied; veto by card name.
