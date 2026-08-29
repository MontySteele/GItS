# P3, graded blind — `opus-5-fresh`

- **grader**: opus-5-fresh (Claude family)
- **slot**: P3, and only P3
- **independence, stated limit**: independent of the rule's STATEMENT (written by another model family), NOT independent of its IMPLEMENTATION (Claude-family). Recorded, not asserted clean.
- **prompt**: `review/qa/kokomi-kurage-blind-001-p3-prompt.txt`

---

## 1. The evidence

**A. Every Muster the tester actually ran, and what it said.** Muster (Rule 1)
was reached six times across the run — `To the Front!` plus its target-and-
confirm screens. Not one of those turns states a Memory consequence. All of
them reason about the *recruit* received, or about the sacrificed card being
worthless, never about the sacrificed card entering the queue at a price:

- `turn-012` — `play "To the Front!"`: "My current block already covers the
  attack, so converting one remaining ordinary card into a discounted companion
  may provide extra damage or utility." → value of the recruit only.
- `turn-014` — `choose "Coral Guard"`: "Current block already covers the
  incoming attack, while Tactical Retreat could still help draw damage, so
  Coral Guard is the better card to transform." → the sacrifice is picked
  because it is the *least useful card in hand*, i.e. treated as discarded, not
  as queued.
- `turn-015` — `confirm`: "Coral Guard is selected for the one-card
  transformation, so I will confirm without selecting Tactical Retreat."
- `turn-021` — `play "To the Front!"`: "Transforming the unneeded Coral Guard
  into a discounted companion may produce enough damage to finish the
  non-attacking enemy this turn."
- `turn-023` — `choose "Coral Guard"`: "The enemy is not attacking, so Coral
  Guard is redundant while Tactical Retreat may still cycle into useful damage."
- `turn-024` — `confirm`: "Coral Guard is the intended one-card transformation
  target."
- `turn-046` — `play "To the Front!"`: "Existing block already covers the only
  attack, so transforming a redundant Coral Guard may provide enough damage to
  finish the Leaf Slime."
- `turn-048` — `choose "Coral Guard (1)"`: "The current block already covers the
  attack, so one Coral Guard is the best transformation target; the two copies
  are indistinguishable here."
- `turn-049` — `confirm`: "One redundant Coral Guard is selected, matching
  Muster 1."

Count of Muster turns that state the Memory consequence: **0**.

**B. Turns that DO state a Memory consequence — but are not a Muster and not a
deliberate Exhaust.** Two turns, both plain plays of a free card:

- `turn-005` — `play "Gorou — Inuzaka All-Round Defense" on "Nibbit"`: "The free
  attack adds damage without consuming energy and **may help establish the
  jellyfish's memory** before I commit the rest of the turn."
- `turn-010` — `play "Shinobu — Grass Ring of Sanctification"`: "The free block
  fully covers most of the incoming attack and **gives the jellyfish a card to
  remember** without spending energy."

These are plays toward the queue and they say so, but neither is a Muster and
neither is stated as an Exhaust; the tester never says "I burn this" or names a
price. They do not satisfy the slot's kind as written.

**C. Near-misses that reason FROM the queue, not INTO it.**

- `turn-006` — `play "Kurage's Oath"`: "The jellyfish is already set to replay
  Gorou next turn, so this power should turn that recurring memory action into
  additional defense." → reads the queue's existing contents; does not put
  anything into it.
- `turn-026` — `end turn`: "…while preserving the current jellyfish sequence."

**D. Fight and run records — the same absence, stated at length.** The Muster
target is repeatedly explained purely as a dead card:

- Fight 2, #4: "Coral Guard became dead on turns with excess block or no
  incoming attack, **making it the natural Muster target**."
- Fight 5, #4: "Coral Guard was useful against the large hit but dead once
  existing block covered the only attack; **Muster then turned it into value**."
- Fight 1, #5: "I shifted from defense toward ending the fight and **testing
  Muster**."
- Run, #2: "a repeated choice between keeping basic defensive cards and
  transforming them into **unpredictable but discounted Companions**."

The single end-of-run sentence that touches the queue at all gets the causal
direction wrong — Run, #1: "The character seems to build Charge by **Exhausting
cards, especially temporary Companions created through Muster**, then use Charge
to strengthen the persistent Bake-Kurage." After sixty turns and six Musters the
tester's model is that Exhaust makes *Charge*, and the sacrificed card entering
the memory is never once articulated.

**E. Contemporaneous complaint that the strip did not teach it.** Fight 1, #6:
"The memory display was somewhat confusing: after Gorou it showed 'Charge 1 / 0,'
then later said the memory was empty despite Charge remaining." Fight 2, #6: "The
memory's 'Coral Guard blocked' entry also said nothing behind it fires, yet Sayu
remained listed behind it, so I could not tell exactly what would replay."
Notably, the "Coral Guard blocked" entry is Rule 1 having fired — the sacrifice
sitting in the queue — and the tester reads it as a display bug, not as a rule.

## 2. Against the threshold

Threshold as written: **at least 3 of 10 graded turns** carry a plan that is a
Muster or a deliberate Exhaust **and states the Memory consequence**, and **at
least one of them is a Muster**. Denominator: 10 graded turns. Falsifier: **0** —
"a run where the tester never once plays toward the queue".

Counting exactly as written, and applying the instruction that a card played for
its printed body alone does not count and that the tester must state the MEMORY
consequence:

- Muster turns stating the Memory consequence: **0**. The mandatory sub-clause
  ("at least one of them is a Muster") therefore fails on its own, independently
  of the count.
- Deliberate Exhausts stating the Memory consequence: **0**. No turn names a burn
  for the queue, and no turn names a price in Charge for a queued card.
- Qualifying turns, total: **0 of 10**.
- Turns that play toward the queue and say so, but are neither Muster nor stated
  Exhaust: **2** (`turn-005`, `turn-010`). These do not meet the slot's kind, but
  they are not nothing.

So the threshold is missed by the full margin, and the Muster sub-clause — the
half of the rule nothing on the card's face says — is at zero across six
opportunities. The falsifier, however, is worded as *never once plays toward the
queue*, and `turn-005` and `turn-010` are plays made explicitly to feed the
memory. On the falsifier's own words the run is not at zero.

## 3. Verdict: **SPLIT**

It cuts both ways, and here is how. On the threshold the slot fails absolutely:
0 of 10 qualifying turns, and 0 Musters carrying a Memory consequence out of six
Musters played — the arm's central bet, that the base kit teaches Rule 1, is not
supported by a single line of the record. But the falsifier as written fires only
at "never once plays toward the queue", and the tester twice plays a free card
for the stated purpose of giving the jellyfish something to remember
(`turn-005`, `turn-010`). Rule 2's direction is faintly legible to a blind
player; Rule 1's is invisible. Graded strictly, that is a threshold failure whose
falsifier does not fire, which is SPLIT rather than MISS — and the split is
between the two rules, not between two readings of one rule.

## 4. Judgment: **RETURN**

The teaching surface for **Rule 1 — the Muster rule, that the SACRIFICED card
enters the memory and not the recruit** — needs rework. The evidence for that is
not an absence of opportunity: the tester reached Muster six times, chose its
target deliberately each time, and every single time chose it on the grounds that
the card was *dead and worth nothing*, which is the exact inverse of the rule. It
then wrote at the end of the run that Exhaust builds Charge. Rule 2's surface
fares better and does not need the same rework — `turn-005` and `turn-010` show a
blind player inferring "a card I play becomes a card the jellyfish remembers"
unaided. The memory strip is also implicated as a teaching surface, not only as a
display: Fight 1 #6 and Fight 2 #6 report the queue's contents as inconsistent
and unreadable, and the one moment Rule 1 was visible on screen ("Coral Guard
blocked") was read as a defect. I name those as what needs rework and stop there;
the dose question the slate raises past this point is not mine.
