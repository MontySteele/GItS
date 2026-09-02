Status: OPEN (draft 6, approved R241 for the Prototype build; the slice is written on it next)

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
2. **Plan.** Some of her cards carry a **Plan:** line: what the jellyfish
   does at the start of your next turn, before you draw, if you play the
   card on the jellyfish instead of where it would normally go. The cost is
   paid now either way. A planned card leaves your hand like any played
   card and nothing takes it back. Her basics are plain cards with no Plan
   line.
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

Every Plan card in hand asks the same question: now, or next turn for
more. The enemy's intent this turn is the price of waiting, the plain
basics are what you spend while the plan cooks, what lands next turn is
the reward, and three Plans written on one turn land together the next
morning before you draw, which is the moment the kit is built around.
Drafts 2 to 5 had a bank (Tide), a second "later" (the exhaust row), and a
healing pillar the law forbids, and each took a keyword and gave no
decision. They are gone. What survives of them: the row's best trick
becomes one Uncommon or Rare (section 6), and the heal becomes one Rare.

## 4. The starter, ten cards, four ids

| Card | Cost | Type | Printed text | Copies |
|---|---|---|---|---|
| Strike | 1 | Attack | Deal 6. | 4 |
| Defend | 1 | Skill | Gain 5 Block. | 4 |
| Kurage's Oath | 1 | Skill | Plan: Deal 5 to every enemy. | 1 |
| Slack Water | 1 | Attack | Deal 4 damage. Apply 1 Weak. Plan: every enemy gains 2 Weak. | 1 |

The basics are the base game's Strike and Defend (R242) and apply no element ([USER], 2026-09-02); her own Attacks apply Hydro the way every catalyst
character's do, which is what a companion's Pyro, Electro or Cryo card
reacts with. Kurage's Oath has no now-line: it is the jellyfish's own
strike and the only way to play it is to plan it. Slack Water is the one
starter card with both lines, so fight one shows the choice once.

Relic, **Tamakushi Casket** (pick 3): the Bake-Kurage is out from the
start of every combat, and whenever you apply a debuff to an enemy, it
strikes that enemy for 2 Hydro damage.

Fight one, turn one: three energy, Water's Edge twice, Coral Guard,
Kurage's Oath, Slack Water; the enemy intends 8. Slack Water on the enemy:
4, Weak, and the jellyfish's 2, the relic's lesson. Coral Guard, 5 Block
against a Weakened 6. Kurage's Oath on the jellyfish. Turn two opens with
the jellyfish hitting every enemy for 5 before you draw. Slack Water was
the decision: blunt this turn's hit now, or 2 Weak on everyone at dawn
with the jellyfish striking each of them. That is the whole kit, on turn
one.

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

1. **The first question, answered in the decompile (2026-09-02): yes.**
   The engine has pets: a creature spawned on the player's side for the
   whole combat that enemies structurally cannot target, since their moves
   only ever aim at players; the Necrobinder's Osty is one. The mod's base
   library ships the seam already: a pet model with its HP bar hidden, and
   a Pet target type with the validation, selection and drag-to-target
   patches in place, so a card can be aimed at the jellyfish unmodified,
   and its play hands the card the jellyfish as the target creature. The
   Bake-Kurage becomes such a pet; her Plan cards target "an enemy or the
   Bake-Kurage" (Attacks) or "you or the Bake-Kurage" (Skills). Effort:
   small to medium, about two days. The risk is the creature's art and its
   placement on the field, which is bespoke code per pet.
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

Planned Attacks hit the front enemy: readable and positional; "a random
enemy" is the Memory arm's rule and a one-line change. Slack Water's
status is Weak, the defensive one; Vulnerable is the one-word swap. Slack
Water carries a Plan line so fight one shows the choice once; dropping it
is a one-line change. The relic's 2 is a number play moves. Tamakushi
Casket replaces the misspelled Tamanooya's. The audit's picks are answered
by this draft and its file moves to `review/ruled/`.

## 9. Picks

1. **How a card becomes a Plan.** (1) Play it on the Bake-Kurage, a pet
   on your side of the field, as you suggested. **Default**; the engine
   supports it (section 7). (2) Plan is a property of certain cards only;
   the starter mixes now-cards and Plan-cards and there is no per-card
   choice. The smaller game, if you would rather not have the choice on
   every card.
2. **The jellyfish's body.** (1) Untouchable: no HP, enemies cannot hit
   it, it is only where a Plan is sent. **Default.** (2) A creature with HP
   that enemies can hit and you can lose, so a plan can be disrupted. A
   bigger game and a much bigger build; not for slice one.
3. **The relic.** (1) Whenever you apply a debuff to an enemy, the
   jellyfish strikes it for 2 Hydro damage. **Default**: live from turn
   one through Slack Water, pays the status Plans the pool will carry,
   and pays reactions too, since Superconduct, Overloaded and Frozen on a
   boss all apply a debuff; the Hydro hit re-wets the enemy for the next
   companion card. (2) Whenever you trigger an elemental reaction, the
   jellyfish strikes that enemy for 3 Hydro damage. The purer reaction
   reward, and dead in fight one, since the starter carries one element
   and no companion. (3) Enemies hit by a Plan gain 1 Vulnerable. Keyed to
   the Plan itself; silent on the turns you spend on basics.
