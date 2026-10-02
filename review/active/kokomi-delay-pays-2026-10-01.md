# Kokomi: the delay pays for itself (2026-10-01)

[USER], 2026-10-01: "that's the recurring challenge of Kokomi - we have an
interesting idea, but how do we make it 'worth' it without just making the
numbers OP."

## 1. What the seats say

Four Sonnet seats on her 78-card build today, two on the 0.2.4112 pool and two
on 0.2.4162 (status batch, "Or plan:", Riptide Ruin). **All four died to the
act-1 boss.** On the same builds and the same seat type, every other run cleared
act 1: base Ironclad, base Silent, three Varka lanes and two Furina lanes.
Records: `review/records/kokomi-pool-round-2026-10-01.md`; the 0.2.4162 pair
is in the session scratchpad (`w9-lane1/`, `w9-lane2/`) until its record lands.

The two newest deaths say the same thing in different words:

- **Plans never answer the attack she is facing.** "Plans land at the start of
  the next turn, so they never answer the attack I am facing ... most turns
  were 'plan, then spend the rest on Strike or Defend'," with about 10 HP lost
  per fight. The other seat: the Matriarch stacked Dexterity −2, then −4, and
  "by round 10 my Defend printed 1 Block, Oath 2 and Barbara 2."
- **What she gets for waiting is offence only.** Plans double, the Casket
  counts, and Sango Isshin scales. Both seats called the Plan turns the best
  turns of the run. Neither died for lack of damage alone: both died bleeding.

Why defensive Plans don't fix it: a Plan is written blind. You can't see next
turn's intent when you write it, so a Block Plan is a guess, and a damage Plan
is never wasted. Seats rationally plan damage and defend with flat 5 to 6
Block cards, which Dexterity and Frail shut off.

## 2. The proposal: the Bake-Kurage shields her while it waits

**One rule, on the Bake-Kurage:**

> It holds your Plans until your next turn. **While it holds them, you have 2
> Block for each Energy you paid for them.**

In practice: when you write a Plan that cost Energy, you gain 2 Block per Energy
at once. Writing Kurage's Oath as a Plan (1 Energy) gives 2 Block now and
7 damage to ALL enemies next turn; writing Surging Shoal (2 Energy) gives 4
Block now and 22 damage next turn.

Why this shape:

- **It pays for the delay where the delay costs:** this turn's defence. A
  waiting Plan is no longer an empty hand slot this turn.
- **It is not a number bump on any card.** It scales with how much she commits
  to planning, which is her identity.
- **0-cost Plans give nothing,** so spamming Nips does not stack Block. Weight
  of the Plan already reads "Energy paid for the Plans waiting", so the count
  exists in the code.
- **It is the jellyfish's Block, not a card's,** so Dexterity and Frail do not
  touch it. That answers the Matriarch death directly: in the base game,
  Dexterity changes Block from cards, not Block from a Power.
- **Lore:** in the source game the Bake-Kurage is her healer. Our law puts
  healing at Rare, so the shield is the summon protecting her.

**Size check.** A seat that plans 2 Energy a turn gets 4 Block a turn, about 16
HP across a four-turn fight. That is roughly the 10 HP per fight the newest seat
bled. Kurage Canopy (Block when a Plan is carried out) and Breakwater (Block per
Plan waiting) become build-arounds on top of a baseline, not the only defence.

**What it costs to test:** a central rule change, so two seats and then you
play her.

## 3. Considered and set aside

- **Plans that read the intent when they land** (Tide Wall and Flank do this
  now). More of these is the earlier record's "delay paper" idea. They are
  good cards, but they need a draw to show up; the death is in every run.
  Keep that as a card batch after this rule is read.
- **Bigger numbers on her Block cards.** That is the "print commons with big
  numbers" patch you rejected for Varka.
- **Open the Casket without Exhaust.** Every record flags "one cash-in per
  fight", but the Strength it gives is permanent, so without Exhaust she would
  get Strength equal to every Plan she ever carried out. That is too much
  alongside a new rule. Re-read it after the shield.

## Picks

1. **The shield rule** (2 Block per Energy paid for waiting Plans, outside
   Dexterity and Frail). (a, default) build it; (b) 3 Block per Energy; (c) no
   rule change, and a card batch of intent-reading Plans instead.
2. **Open the Casket.** (a, default) unchanged until the shield is read;
   (b) drop its Exhaust now.
