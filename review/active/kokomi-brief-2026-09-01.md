Status: OPEN (draft 7; the live Paper artefact for the Prototype build, carrying R241, R242, R250, R265, R266, R267, R268 and R276)

# Kokomi overhaul brief, draft 7: the Plan

Draft 7, 2026-09-08, under R267. Draft 6 (2026-09-02, approved R241) is
retrievable from git; this draft changes no ruled direction and adds the
rules ruled since: the Kurage's Oath now-line (R250), Dusk and the queue as
a resource (R265), the cap retired (R266), and Slack Water and Scout Ahead
restored (R267). The ruled direction (R240) is unchanged: Plan is Kokomi's
key idea and goes into the starter deck; reusing Exhausted cards is a payoff
card, not the chassis; Mend is a thing she can do, not a premise.

**The brief is the design record.** A pool pass may move a pool row's
numbers and shape under the pass-three charter (§8), but a rule in §2, a
starter card in §4, or the turn-one decision in §4 moves only by a ruling.
Pass five's move of Slack Water's Plan to Dusk (2026-09-08) was applied as a
default against this page and is reversed by R267; that is why this
paragraph exists.

## 1. The character in one line

Sangonomiya Kokomi wins the fight before it starts. She writes the plan;
the Bake-Kurage carries it out at the start of her next turn.

## 2. The rules

1. **The Bake-Kurage** is on your side of the field for the whole combat.
   It is not a fighter and enemies cannot touch it. It is where a Plan is
   sent.
2. **Plan.** Some of her cards carry a **Plan:** line: what the jellyfish
   does at the start of your next turn, after your draw and after the
   turn's Block and Energy reset, if you play the card on the jellyfish
   instead of where it would normally go. (Both engines resolve after the
   draw on purpose: a Plan that resolved before the reset would lose its
   Block and Energy to it.) The cost is paid now either way. A planned card
   leaves your hand like any played card, and only a card that says so
   takes it back (Second Thoughts, rule 6). **Her basics are the base
   game's Strike and Defend and carry no Plan line (R242); they are never
   changed ([USER], 2026-09-08).** The Plan line prints on its own line,
   under the now-line ([USER], 2026-09-28: "The idea of Plan cards makes
   sense, but the card text gets harder to read. Can we move all Plan
   lines to the next line down?"); the generator breaks it, not the sheet.
3. **The jellyfish acts by the book.** A planned Attack strikes the front
   enemy (the leftmost one alive); a single-target Plan is aimed when
   written if the engine can carry a second selection (R250). A planned
   Skill acts on you unless its Plan line names enemies (Kurage's Oath's
   does). Plans are carried out in the order they were written,
   and your Strength and Dexterity count, since the plans are hers.
4. **Nothing happens by itself.** No bank, no pulse, no automatic replay.
   If the jellyfish is doing something, a card you played and paid for told
   it to.
5. **Dusk (R265 trial, still on).** A card whose Plan line says **Dusk**
   is carried out at the end of this turn, before enemies act, instead of
   the next morning. It is the kit's only "protect now" written line and
   is a pool shape, not a starter one.
6. **The queue is a resource (R265).** Pool rows may read the queue (how
   many Plans wait, which is first), reorder it, hurry it (Change of Plans
   carries out the first Plan now) or cancel it (Second Thoughts returns
   the last Plan's card and cost). No cap on the queue: R266 retired the
   two-Plan cap as a rule; a free turn is priced by the faces, not by a
   throughput limit.
7. **The Casket counts (2026-09-28).** Her relic, the Tamakushi Casket,
   gains 1 each time the Bake-Kurage carries out a Plan -- in the morning,
   at Dusk or hurried by Change of Plans, and a Plan carried out twice adds
   twice. The count is per combat and starts at 0. Open the Casket (a 0-cost
   Retain, Exhaust token the relic puts in her opening hand) turns the count
   into Strength, 1 per point, and empties it; the Casket keeps counting.
   Cards may read or add to the count; none spends it. [USER]: "We don't
   need this to be the equivalent to Regent's stars or Klee's sparks. This
   should feel like a distinct effect."

Two printed keywords: Plan and Dusk. Mend appears only on Rare Exhaust
cards, as the healing law already has it (`LAW.md`, card-sheet rules).

## 3. The decision, and why the old drafts had none

Every Plan card in hand asks the same question: answer this turn, or
buy something only a head start can buy. The enemy's intent this turn is
the price of waiting, the plain basics are what you spend while the plan
cooks, what lands next turn is the reward, and three Plans written on one
turn land together the next morning, after you draw, which is the moment
the kit is built around.

**The halves rule (R276 pick 1).** The now-line answers this turn; the
Plan line buys something only a head start can buy. The two halves are
never the same effect at two sizes. When "later" was the same thing but
bigger, the only reason to play a card now was this turn's incoming
damage, so a safe turn had one right play: write everything ([USER],
2026-09-23: "generally not a choice so much as a math problem"). A
now-line does what matters this turn (draw or filter, a debuff that
multiplies this turn's plays, Block, a kill); a Plan line does what is
worth more for being early (Energy or cards for tomorrow, a debuff up
before the next swing, Block sized to the next attack, a board read).
Drafts 2 to 5 had a bank (Tide), a second "later" (the exhaust row), and a
healing pillar the law forbids, and each took a keyword and gave no
decision. They are gone.

A hand of basics has no Plan decision in it, and that is by design: the
kit's question arrives at the first Plan card. Where that is answered was
ruled R268 (2026-09-08, `review/ruled/kokomi-plan-less-hand-2026-09-08.md`):
nowhere for now, and the next seat round reads the depth of the pool's Plan
interactions before any access card is drafted. It is never answered by
touching the basics.

## 4. The starter, ten cards, four ids

| Card | Cost | Type | Printed text | Copies |
|---|---|---|---|---|
| Strike | 1 | Attack | Deal 6. | 4 |
| Defend | 1 | Skill | Gain 5 Block. | 4 |
| Kurage's Oath | 1 | Skill | Gain 6 Block. Plan: Deal 7 damage to ALL enemies. | 1 |
| Slack Water | 1 | Attack | Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies. | 1 |

The basics are the base game's Strike and Defend (R242) and apply no
element ([USER], 2026-09-02); every damaging card of her own applies Hydro,
Skills included (R276 pick 2), which is what a companion's Pyro, Electro or
Cryo card reacts with. Kurage's Oath gained a now-line under R250 pick 1
(round 4d), so writing it is a trade rather than the only play; R276 pick 1
made that line 4 Block, a different job from the Plan's 7 to ALL (the
halves rule, §3). 2026-09-28, [USER]: "The non-plan effect is quite bad
(worse than a basic defend)" ... "Option 1 is fine for now." The now-line
is 6 Block, and the upgrade moves both halves: 8 Block, Plan 10 to ALL.
Slack Water's Plan is a **morning** Plan: the Weak lands the
next turn, after the swing it was written against, and that delay is the
point (R267 pick 1). Its numbers are the R243 audit's (Weak 1 now, Weak 1
to ALL written; upgrade 7 damage and 2 Weak written).

Relic, **Tamakushi Casket** (the Casket pass, 2026-09-28): "Start each
combat with the Bake-Kurage and Open the Casket in hand. Each Plan it
carries out adds 1 to the Casket." Open the Casket: "Gain Strength equal to
the Casket's count, then empty it." (0, Retain, Exhaust.) [USER], choosing
this Forge-style relic over a Vigor-style one, because Vigor "devolves into
'solve for lethal, press the I Win button'": "an artifact that grants /
tracks an alternative energy that builds by 1 for every Plan played, and
adds one 0-cost Retain / Exhaust card that converts that energy into
Strength. We could build other archetypes in, including some that read or
modify the gauge." Counting is "when it's carried out"; "1 strength per
point seems fine; we can adjust down if we need to"; "the casket keeps
counting." The relic's old debuff strike (2 Hydro per debuff she applied)
is gone. It keeps the companion reward slot.

Fight one, turn one: three energy, Strike twice, Defend, Kurage's Oath,
Slack Water, and Open the Casket held for later; the enemy intends 8.
Slack Water on the enemy: 4 and Weak. Defend, 5 Block against a Weakened
6. Kurage's Oath on the jellyfish, or 6 more Block now. Turn two opens
with the jellyfish hitting every enemy for 7 once you have drawn. Slack
Water and the Oath were the decisions: blunt this turn's hit now, or Weak
on everyone and 7 to everyone at dawn. That is the whole kit, on turn one.

## 5. The payoff moment

The morning the Plans land. The pool pays for it twice over: cards that
read the carry-outs (Feint and Sango Isshin pay per Plan carried out this
turn since the Casket pass; the Casket itself counts every one, and Open
the Casket turns the count into Strength), and her Burst, **Nereid's Ascension** (Rare Power, 2): the jellyfish carries
out your **first** Plan each turn twice (pass three; "every Plan twice"
paid for writing more, which is the shape the pool passes undo). It is the
one Rare that bends rule 3's "once, in order," and it makes the order of
the queue the decision.

## 6. The pool, in one line per loop

- **The Tactician.** Plans and the cards that pay per Plan carried out.
  Payoff: the morning. The order riders (Opening Gambit doubles the next
  Plan, Second Wave repeats it, Scout Ahead draws one per **later** carry-out
  in the same drain, R267 pick 3) make writing order the puzzle.
- **The Priestess.** Block through the jellyfish, Dusk for the turn the hit
  is on; Mend only at Rare and Exhaust. A thing she can do.
- **The Commander.** Gorou and the Inazuma companions (R236); how a
  companion meets the jellyfish is the slice's question, and no play is
  free.
- **The replay, demoted.** One Uncommon or Rare, Moon's Reflection:
  Exhaust; choose a card in your Exhaust pile; next turn the jellyfish
  carries out its Plan line. Good design space, never the chassis.
- **The Casket (2026-09-28).** Cards that read or add to the count: Pearl
  Diver (Plan: the Casket gains 2), Moon Signal (the Casket gains 1 when 2 or
  more Plans wait at the start of her turn), Driftglass and Depths' Judgment
  (damage off the count), What the Tokoyo Took (double it) and What the
  Tokoyo Returns (Open the Casket back from the Exhaust Pile).

THE POOL (the Casket pass, 2026-09-28): 46 offered cards, 24 Common, 17
Uncommon, 5 Rare, plus the three co-op cards
(`KokomiOverhaulRoster.Slice()`, `C.KOKOMI_OVERHAUL_POOL_IDS`). Cut: Tide
Chart, Cleansing Wave, Ripple, Well Laid, Sea-Salt Prayer, Salt Line.
Added: Massed Volley, Signal Arrow, Surging Shoal, Pearl Diver, Press the
Advantage, Shell of Sanctuary, Driftglass (Common); What the Tokoyo
Returns, Depths' Judgment, Tideturn, Moon Signal, Pearl Current (Uncommon);
What the Tokoyo Took (Rare). Second Wave moved to Uncommon. On the Commons,
[USER]: "Let's avoid having too many attack / block spam cards ... they
shouldn't just be 10 copies of 'do x damage, or plan y'"; "5 to 7 damage per
1 energy is roughly the going rate on AoE commons". Numbers and faces:
`docs/notes/prototype-surface-provenance.md`, "the Casket pass".

Rares take constellation names (C1 to C6 are all unused but Sango Isshin
and The Clouds Like Waves). Cut and not coming back: Tide, Surge, Exert,
the pulse, Orders, Tactics, Spent, Garment as a keyword, Flawless Strategy,
the two-Plan cap (R266), Night Watch and Converging Tide (retired on the
pool passes), The Moon Overlooks the Waters (withdrawn at the door, 2026-09-05).

## 7. What the engine does

1. The Bake-Kurage is a pet on the player's side (the base library's pet
   seam), targetable by her Plan cards and by nothing else.
2. The typed Plan queue (`Powers/Prototype/KokomiPlan.cs`, `tier0/engine/kokomi_plan.py`)
   holds morning and Dusk entries, resolves each drain in order, and carries
   the first entry twice under the Ascension.
3. The strip draws the pending Plans face up, in order, on the jellyfish,
   and the jellyfish panel prints "No Plan card in hand: the jellyfish
   waits" on a hand of basics.
4. Retired under the flag: Tide, Surge, Exert, the pulse, the Garment
   power, Strength to Tide. The shipped 76-card Kokomi is untouched.

## 8. The pool-pass charter (from pass three, 2026-09-07)

A pool row may change on a pass only inside these clauses, and a pass with
a card change goes to the doctrine door before a tester: C1 no row removes
a losing line the kit is meant to keep instead of pricing it; C2 a benefit
carries a binding price; C3 the card's value is decided by a choice the
player makes; C5 nothing fires by itself; C6 no row is strictly better than
a pool row or a base-game card at its rarity and cost; C7 a Common never
increases deck size; C8 the two halves of a Plan card are never the
same effect at two sizes: the now-line answers this turn and the Plan
line buys what only a head start can buy (R276 pick 1, §3). Both halves of
a two-half card must be worth playing on some turn. Passes four and five went to the door on 2026-09-08 under
R267 (`review/records/kokomi-pass-four-audit-2026-09-08.md`, `-five-`).

## 9. Applied defaults (D/E/F, disclosed, yours to veto)

Planned Attacks hit the front enemy or the aimed one. Slack Water's status
is Weak, the defensive one. The Casket's 1 per Plan and 1 Strength per point
are numbers play moves. Tamakushi Casket replaces the misspelled
Tamanooya's.

## 10. Picks

None open on this page. Picks 1 to 3 of draft 6 (a card becomes a Plan by
being played on the pet; the pet is untouchable; the relic strikes on a
debuff) were ruled R241 at their defaults; the third was replaced by the
Casket pass (2026-09-28), rule 7 above.

Not yet ruled, found while building the Casket pass: Shell Guard's face
("whenever the Tamakushi Casket strikes, gain 3 Block") names the strike
the pass removed, so its second clause no longer fires.
