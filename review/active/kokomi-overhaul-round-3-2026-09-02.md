Status: OPEN (round three: the rules gate passed on your act-1 run; two legibility rows; one pick on the depth axis for acts 2 and 3)

# Kokomi overhaul, round three: the rules gate, and what scales

2026-09-02. Round two's build (0.2.2083+proto.dirty, main 3f6157c0) was
your fresh run of the Plan rules: the Bake-Kurage as a pet, a card
played on it carried out at the start of your next turn, the Tamakushi
Casket striking for 2 Hydro on a debuff. You cleared act 1. This packet
reads your four answers beside the Opus round-3 seat
(`review/qa/blindplay/kokomi-overhaul-r3-opus/record.md`, 38 actions,
two fights) and the balance record
(`review/records/balance-read-prototype-2026-09-02.md`).

## 1. The rules gate, passed

Your answers, a sentence each, against the round-2 questions:

1. **Now or at dawn came up as a choice**, often: "block now / kill an
   enemy now, vs set up Plans for the next turn." That is the brief's
   contested thing on the table, in your words.
2. **Mornings paid off**, "especially the long-term status effects or
   strong AoE hits." The multi-target and the debuff Plans are where the
   morning is worth the wait; the single-target damage Plans are not,
   which is the Opus seat's read too ("the Plan is a tax" against one
   enemy, Oath at 5 next turn against a Strike's 6 now).
3. **The casket's strikes registered but did not feel natural**: "some
   damage would happen and then I would have to remind myself why." The
   Opus seat saw the same from the other side: the jellyfish's only
   strike "did not register as an event at all: no line, no
   announcement," just the enemy's HP lower.
4. **No card you never wanted to play**, though you skipped cards at
   the reward screen you would not have wanted; the seat's never-wanted
   was Coral Guard, which the base Defend has since replaced (R242).

So the Plan rule stands at Prototype. What round two owed you is
built: the R243 numbers (Treatise, Song of Pearls and the Banner once
per turn; Sango Isshin paying only on a morning you planned for; The
Moon, A Ship at 3 and 6), the upgrade path for every Plan card
(EB-315), and the base Strike applying nothing. Battle Plan and
Vanguard stay watch items: neither the seats nor you named them as the
play every time, so they are unchanged, and the three-act seat runs
below are their next read.

## 2. Two legibility rows, filed

- **`EB-316`, the casket hit has no moment.** When the Bake-Kurage
  strikes for 2 off a debuff, the number lands inside the card's own
  damage and nothing says the jellyfish did it. The fix is a visible
  beat: the pet's strike animates, the hit prints as its own number, and
  the enemy's tooltip names it. Your "remind myself why" and the seat's
  "no line, no announcement" are the same defect.
- **`EB-317`, the morning has no announcement.** At the start of your
  turn the Plans are carried out and the panel simply reads empty. The
  fix is a carry-out moment per Plan: the pet acts, a line names the
  card and the number ("Bake-Kurage: Ambush, 12"), the queue empties in
  view. Round two's Opus seat asked for this; round three's saw the
  same.

Both are C# surface work with no rule change, built for the next
deploy.

## 3. The Rares and the numbers, one paragraph

The shop that sold four Rares and the two before the boss were the base
game's own rarity roll, which is a pity system: your log shows the rare
threshold climbing a point per non-rare offer and the shop's base
higher than a reward's, and the boss reward forced. The mod adds only
its two Companion shop slots at Uncommon-or-Rare. Itto (14 damage and
12 Block for 2, no setup) is the shape you rejected on Sango; it is the
companion workshop's, noted there with your words.

## 4. Acts 2 and 3: the depth axis

Your takeaway: "it's easy to generate big numbers, which basically
solves act 1, but we'll need to make sure that there's enough complexity
/ combo optimization to scale to acts 2 / 3." Today the kit scales three
ways: more energy means more Plans a turn (Battle Plan, Sucrose), the
debuff Plans stack Weak and Vulnerable that the casket converts, and the
Rares double the morning. None of those makes the NUMBER of Plans you
set up matter on its own, and that number is the thing the tension in
your answer 1 is about: every Plan costs a now. The pick below is which
axis to build for round four; the seats read it three acts deep before
you play it.

## 5. Picks

1. **What the morning scales with.** (1) **Momentum** [default]: the
   Bake-Kurage carries out Plans in order, and each Plan after the first
   in the same morning is carried out with 2 more (damage, Block or
   Mend; a debuff Plan applies 1 more). One rule on the pet, printed on
   its badge, no new card; the queue's length becomes the payoff, so
   setting up two Plans at the cost of two nows is a different decision
   from one, and it grows with energy into act 3. The 2 is a D default.
   (2) **Counting cards**: three new rows that count Plans carried out
   this combat (a Rare "Plan: deal 3 for each Plan carried out this
   combat", an Uncommon Power "at the start of your turn, if three or
   more Plans were carried out this combat, gain 1 Energy", a Common
   that draws 1 per Plan carried out this morning). Classic combo
   depth, more surface, drafted rather than given. (3) Both, momentum
   as the rule and one counting Rare.
2. **Your next Kokomi play.** The base Strike's exemption is a rule
   change, so the round-three build is yours. (1) **Play it after the
   seats' three-act read** [default], one run as far as it goes, with
   one question: on which floor did the mornings stop being enough.
   (2) Play it now, before the seats.
