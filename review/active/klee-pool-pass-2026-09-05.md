Status: OPEN (no pick; the defaults in §5 are applied; ten rows to the audit door)

# Klee pool pass one: a detonator you can keep, and the shelves the rounds found thin

Written 2026-09-05 from the readings rounds 13 to 16 carried to "the pool
pass" (`review/active/klee-overhaul-round-13-2026-09-04.md` to `-16-`), read
against the brief (`review/active/klee-brief-2026-09-01.md`, §5 to §9) and
the pool as it stands (`docs/prototype-surface.yaml`, 35 `proto_ko_` rows).
Prototype stage: no slate, no stamp, no number here is quotable. Every row
below goes through the doctrine audit before a tester sees it
(`review/records/card-audit-2026-09-04.md` §5.3), and the ones that come
back FOLLOWS are built in C# first and granted or drafted in round 17 on.

## 1. What the rounds said, in one paragraph each

**Hold or fire needs a card that stays in hand.** Round 15: with Ka-pow!
undrawn until fight one's third turn and every drafted detonator
discarding at end of turn, "hold the Bomb" meant "throw the detonator
away" for most of a run, and a 55-gold Steady enchantment on Perfect
Timing "opened more decision-space than any card I drafted". Round 16,
from the other end: once a pile passes the enemy's HP, Ka-pow! is free and
Retained, so the last turn is automatic, "charming twice, likely corrosive
by the tenth time". The two are one question: the kit has exactly one
Retained detonator, it is free, and it is one card in ten.

**Sparks 'n' Splash, two reads that disagree.** Round 10 drafted it and
played it as R250 pick 1 intends (held the Splash, kept detonating). Round
15 was granted it and never played it in four fights, "correctly each
time". One round each way on a ruled card is not the new fact a re-ask
needs. It stays as built.

**Countdown is quiet.** Played once in six offers. A Common that does what
it says and rarely changes a turn. The checklist's sixth check allows a
plain card; it stays.

**Catalytic Converter is dead in a mono-Pyro deck**, by its own printed
admission. R244 pick 2 ruled Witches' Circle dead alone on purpose, drafted
only by a deck that already holds witches; the Converter is the same shape
for appliers, and its face says so. It stays. What the React shelf lacks
is rows with a floor, below.

**Smoggy switches Klee off** (round 13): one Skill per turn against a kit
whose placers are Skills by rule. The question carried was whether one
placer should be an Attack. Fish-Flavored Bait and Bang Bang! already are;
one more, on all enemies, is below.

**The starter's bottom** (rounds 11 to 16): Strike and Defend are dead by
floor 10. Ruled 2026-09-02 (the basics are supposed to be bad); not a pass
item.

## 2. The ten rows

Rarity, energy, Spark price if any; the pool row each is priced against.
Growth is 4 per turn (`KLEE_OVERHAUL_BOMB_GROWTH`).

**Cook**

1. **Long Fuse** — Common Attack, 1 energy, Retain. *Set off. Deal 6
   damage. Retain. Costs 1 more each turn it stays in your hand.* Upgrade:
   9 damage. Against Sizzle (1 energy: Set off, 6, +6 on a reaction): the
   same body, the reaction line traded for Retain, and holding it one turn
   grows the Bomb by 4 and the card's price by 1. Holding is a bet the
   enemy's intent prices, which is the brief's §4 sentence as a card.
2. **All of My Treasures!** — Rare Skill, 1 energy, Exhaust. *Place a Bomb
   on the enemy equal to your largest Bomb.* Against Careful Arrangement
   (Uncommon, 1: merge and +5): a second pile the size of the first, once.
   Playing it on a 12 or waiting for a 16 is the cook decision, and the
   copy grows on its own schedule (rule 9, each Bomb grows separately).
   Built under `EB-491`, which is the register row this whole §2 waits on.
3. **Fish Blasting** — Common Attack, 1 energy. *Deal 5 damage to ALL
   enemies. Shuffle a Confiscated into your draw pile.* The lore card,
   kept as the brief says (§2, "AoE with a cost card"). Cook's plain
   pressure without a Set off, beside Pocket Fireworks (1: 9 to one).
   Against Cleave (1: 8 to ALL): 3 less and a dead draw later.

**Spray**

4. **Pocket Match** — Common Attack, 0 energy, 1 Spark, Retain. *Set off.
   Deal 5 damage.* Fwoosh! (1 Spark: Set off, 6) with Retain and 1 less
   damage. Round 16's turn one, Bang Bang! unplayable at 1 Spark and no
   Set off in hand, is what it is for: the starting Spark pays it.
5. **Bombs Away!** — Common Attack, 1 energy. *Deal 3 damage to ALL
   enemies. Place a Bomb 2 on ALL enemies.* The Attack placer the Smoggy
   reading asked for. Against Mine Toss (1, Skill: Mine 4 on ALL): a hit
   now and half the charge, no Mine. Against Cleave: 5 less now, 2 per
   enemy cooking toward a Tinder Toss or a Rapid Fire.
6. **Fireworks Show** — Uncommon Skill, 0 energy, 2 Sparks. *Set off ALL
   enemies.* Against Tinder Toss (1 Spark: two random Set offs with 4
   damage each) and Quick Fuse (1 Spark: +3 and Set off one enemy): twice
   the price, no damage, every enemy. Against one enemy it is a worse
   Quick Fuse, which is the losing line.

**React** (each with a floor; the archetype is companion-fed by pick 7)

7. **Kindling** — Common Skill, 0 energy. *Each Bomb on an enemy whose aura
   is not Pyro grows by 4. If there is none, your largest Bomb grows by 2.*
   Against Chain Fuse (1: each Bomb on the enemy +6): free, +2 alone, +4
   per Bomb on every foreign aura when an applier went first.
8. **Flash Point** — Uncommon Attack, 1 energy. *Set off. Deal 7 damage. If
   a Bomb triggered an Elemental Reaction this turn, gain 1 Spark and draw
   1 card.* Beside Perfect Timing (1: 8, replay on a reaction) and Sizzle:
   a tempo rider where those pay damage.
9. **Vermillion Pact** — Rare Power, 2 energy. *Whenever one of your Bombs
   triggers an Elemental Reaction, the Attack that Set it off triggers one
   too.* The brief's §5.3 rule-breaker: the shared "one aura, consumed by
   the first hit" rule is broken for her chain. Dead alone, as Witches'
   Circle is (R244 pick 2); the third of the brief's three rule-breaking
   Rares, and the pool's eighth Rare.

**Bridge**

10. **Split Charge** — Uncommon Skill, 1 energy. *Split your largest Bomb
    into two halves on random enemies.* Careful Arrangement's opposite.
    Alone against one enemy: two piles growing 4 each instead of one
    growing 4, for a card and an energy, and two smaller hits into Block
    where one big one was. On a hallway: a cooked pile becomes Spray's
    fuel, one half landing wherever it lands.

Pool after the pass: 45 rows, Rares 8 (the brief's count), Cook 17,
Spray 15, React 7 with the three Hexerei readers beside them.

## 3. What the pass does not do

No defence row: R252 set the shelf at three conditional rows. No starter
change: R242. No Sparks 'n' Splash change: §1. No Retain on Bang Bang! or
Fwoosh!: two Retained detonators in the Commons is the density the
reading asked for, and a third free one would make round 16's automatic
turn the whole game. Nothing here is a number pick; every figure is a
starting point the seats move.

## 4. The audit and the build

The ten rows go to the doctrine role as ten arms with the charter, the
engine paragraph and the pool census pasted from the sheet, and the reply
is recorded verbatim in `review/records/card-audit-2026-09-04.md` §5.3. A
REQUIRES_MODIFICATION row is rewritten or withdrawn there, never argued.
FOLLOWS rows are built C# first (stage-gate), on new ops where the
engines lack one (a rising hand cost, Set off ALL, a bomb split, an
aura-keyed grow, the Pact's re-react, the Treasures copy), then the tier0
twin, then the surface; round 17 grants what the draft does not offer.

## 5. Defaults applied (D and E), disclosed

- **E:** the pass is ten rows, not the brief's full sixty. The brief's own
  §7.4 says stop at the number that is live; each round tests three to
  five new rows at most, and the next pass writes against what these do.
- **E:** Sparks 'n' Splash, Countdown and Catalytic Converter stay as built,
  with the readings above recorded and no row minted.
- **D:** every number on the ten faces is the pricing shown in §2 and moves
  on the seats' word.
- **E:** one register row for the build (`EB-491`), minted when the audit
  returns; the rows that fail it are withdrawn in this packet's §2.
