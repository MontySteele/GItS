Status: OPEN (draft 6, Paper; the Plan is the chassis, R240; read before the slice)

# Kokomi overhaul brief, draft 6: the Plan

Draft 6, 2026-09-02. Ruled direction (R240): Plan is Kokomi's key idea and
goes into the starter deck; reusing Exhausted cards is a payoff card, not
the chassis; Mend is a thing she can do, not a premise. Everything the
earlier drafts carried beside the one idea is cut here, and this page says
where each cut thing went. The fresh audit that led here is
`review/ruled/kokomi-audit-2026-09-02.md`.

## 1. The character in one line

Sangonomiya Kokomi wins the fight before it starts. She writes the plan;
the Bake-Kurage carries it out at the start of her next turn.

## 2. The rules

1. **The Bake-Kurage** is on your side of the field for the whole combat.
   It is not a fighter and enemies cannot touch it. It is where a Plan is
   sent.
2. **Plan.** Her cards print two lines: what the card does now, and after
   **Plan:** what the jellyfish does at the start of your next turn, before
   you draw, if you play the card on the jellyfish instead. The cost is paid
   now either way. A planned card leaves your hand like any played card and
   nothing takes it back.
3. **The jellyfish acts by the book.** A planned Attack strikes the front
   enemy (the leftmost one alive). A planned Skill acts on you. Plans are
   carried out in the order they were written, and your Strength and
   Dexterity count, since the plans are hers.
4. **Nothing happens by itself.** No bank, no pulse, no automatic replay.
   If the jellyfish is doing something, a card you played and paid for told
   it to.

One printed keyword: Plan. Mend appears only on Rare Exhaust cards, as the
healing law already has it (`LAW.md`, card-sheet rules).

## 3. The decision, and why the old drafts had none

Every card in hand asks the same question: now, or next turn for more.
The enemy's intent this turn is the price of waiting; what lands next turn
is the reward; and three Plans written on one turn land together the next
morning before you draw, which is the moment the kit is built around.
Drafts 2 to 5 had a bank (Tide), a second "later" (the exhaust row), and a
healing pillar the law forbids, and each took a keyword and gave no
decision. They are gone. What survives of them: the row's best trick
becomes one Uncommon or Rare (section 6), and the heal becomes one Rare.

## 4. The starter, ten cards, four ids

| Card | Cost | Type | Printed text | Copies |
|---|---|---|---|---|
| Water's Edge | 1 | Attack | Deal 6. Plan: Deal 9. | 4 |
| Coral Guard | 1 | Skill | Gain 5 Block. Plan: Gain 8 Block. | 4 |
| Stolen Chapter | 1 | Skill | Draw 1. Plan: Draw 3. | 1 |
| Kurage's Oath | 1 | Skill | Plan: Deal 5 to every enemy. | 1 |

Kurage's Oath has no now-line: it is the jellyfish's own strike and the
only way to play it is to plan it. Relic, **Tamakushi Casket**: the
Bake-Kurage is out from the start of every combat, and the first Plan you
write each combat is carried out at once.

Fight one, turn one: three energy, Water's Edge twice, Coral Guard twice,
Kurage's Oath; the enemy intends 8. Water's Edge on the jellyfish lands 9 at
once, the relic's lesson. Coral Guard on yourself, 5 Block, because the 8 is
now. Kurage's Oath on the jellyfish. Turn two opens with the jellyfish
hitting every enemy for 5 before you draw. The second Coral Guard was the
decision: 5 now, or 8 the turn after. That is the whole kit, on turn one.

## 5. The payoff moment

The morning three Plans land at once. The pool pays for it twice over:
cards that trigger whenever the jellyfish carries out a Plan (draw one,
gain Block, hit the front enemy), and her Burst, **Nereid's Ascension**
(Rare, 2, Exhaust): Plan: for two turns the jellyfish carries out every
Plan twice. That is the Ceremonial Garment as one card, and the one Rare
that breaks rule 3's "once, in order."

## 6. Later: the pool, in one line per loop

- **The Tactician.** Cheap Plans and the cards that pay per Plan carried
  out. Payoff: the morning.
- **The Priestess.** Block through the jellyfish; Mend only at Rare and
  Exhaust (Watatsumi's Blessing: Exhaust. Plan: Mend 12). A thing she can
  do.
- **The Commander.** Gorou and the Inazuma companions (R236); how a
  companion meets the jellyfish is the slice's question, and no play is
  free.
- **The replay, demoted.** One Uncommon or Rare, Moon's Reflection:
  Exhaust. Choose a card in your exhaust pile; Plan: the jellyfish carries
  out its Plan line. Good design space, never the chassis.

Rares take constellation names (C1 to C6 are all unused but Sango Isshin
and The Clouds Like Waves). Cut and not coming back: Tide, Surge, Exert,
the pulse, Orders, Tactics, Spent, Garment as a keyword, Flawless Strategy.

## 7. What the engine has to do

1. **The first question, answered in the decompile before anything is
   built:** can a card be aimed at a creature on the player's side? The
   source game's Necrobinder fights beside a summoned creature, Osty, so an
   ally on the field exists; whether her cards can target it is what the
   build checks first. Yes: the Bake-Kurage becomes such a creature, with
   no HP bar and no enemy targeting, and her Plan cards target "an enemy or
   the Bake-Kurage" (Attacks) or "you or the Bake-Kurage" (Skills). No:
   pick 1's second option.
2. The typed Plan queue exists (`Powers/Prototype/KokomiPlan.cs`: seven
   clauses, resolved at the start of her turn before the draw, per player,
   with a pending-count badge). It gains the starter's four clauses and a
   "twice" flag for the Burst.
3. The strip that drew the Memory arm's queue (EB-198) draws the pending
   Plans face up, in order, on the jellyfish.
4. Retired under the flag: Tide, Surge, Exert, the pulse, the Garment
   power, Strength to Tide. The shipped 76-card Kokomi is untouched.
5. The slice, written after you have read this: the ten-card starter and
   about twenty-four pool cards on the three loops, then the Prototype
   gate as before: seats first, then one act-one run by you.

## 8. Applied defaults (D/E/F, disclosed, yours to veto)

The Plan rate is about half again (9 for 6, 8 for 5), a number play moves.
Planned Attacks hit the front enemy: readable and positional; "a random
enemy" is the Memory arm's rule and a one-line change. The relic's
first-Plan-now is the teaching device. Tamakushi Casket replaces the
misspelled Tamanooya's. The audit's picks are answered by this draft and
its file moves to `review/ruled/`.

## 9. Picks

1. **How a card becomes a Plan.** (1) Play it on the Bake-Kurage, a target
   on your side of the field, as you suggested. **Default**, subject to the
   engine question in section 7. (2) Plan is a property of certain cards
   only; the starter mixes now-cards and Plan-cards and there is no
   per-card choice. The fallback if the engine says no.
2. **The jellyfish's body.** (1) Untouchable: no HP, enemies cannot hit
   it, it is only where a Plan is sent. **Default.** (2) A creature with HP
   that enemies can hit and you can lose, so a plan can be disrupted. A
   bigger game and a much bigger build; not for slice one.
