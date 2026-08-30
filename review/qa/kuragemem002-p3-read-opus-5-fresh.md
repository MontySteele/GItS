# P3, graded blind — `opus-5-fresh`

- **grader**: opus-5-fresh (Claude family)
- **slot**: P3, and only P3
- **independence, stated limit**: independent of the rule's STATEMENT (written by another model family), NOT independent of its IMPLEMENTATION (Claude-family). Recorded, not asserted clean.
- **prompt**: `review/qa/kuragemem002-p3-prompt.txt`

---

## 1. The evidence

Turns that carry a plan of the kind P3 describes — a Muster or a deliberate Exhaust **with the memory consequence stated** — quoted verbatim, with the turn each came from.

**`turn-014` — `play "To the Front!"` — COUNTS (Muster).**
> "With no incoming attack and no energy left, Muster can convert an otherwise unplayable card into a discounted Companion and build the memory engine."

This is a Muster played, in the tester's stated reasoning, *for* the queue: the Companion is named, and so is "build the memory engine." Not the printed body alone. The fight-1 record corroborates the intent in the tester's own words: "with only the buffing enemy left, I used To the Front! to develop the memory engine."

**`turn-018` — `play "Gorou — General's War Banner"` — COUNTS (deliberate Exhaust, Rule 2).**
> "The free Companion adds Block, strengthens the next attack, and should Exhaust to build Charge for the queued memories."

The memory consequence is explicit and it is the *pricing* half: Exhaust to bank Charge **for the queued memories**. This is the second of P3's two named example phrasings ("I burn this to bank the Charge for the front") almost word for word.

**`turn-036` — `play "Gorou — Inuzaka All-Round Defense" on "Seapunk"` — COUNTS (deliberate Exhaust, Rule 2).**
> "The free attack deals damage, Exhausts to generate Charge, and queues a free memory replay for next turn."

Names the entry, its route into the queue (Exhaust), and its price band ("free"). Both the deposit and the payment are stated.

**`turn-052` — `play "Gorou — Inuzaka All-Round Defense" on "Sludge Spinner"` — COUNTS (deliberate Exhaust, Rule 2).**
> "This converts Sara's buff into 10 free damage and Exhausts to start building Charge and memory."

Damage is the printed body; "Charge and memory" is the stated consequence beyond it. Counts.

**`turn-058` — `play "To the Front!"` — COUNTS (Muster).**
> "Muster can turn the slower power into a free Companion while preserving the last energy for Water's Edge, potentially adding immediate value and more Charge."

The turn sentence names Charge but not the word "memory". The tester's own fight-4 record, written for the same action, supplies the memory clause verbatim:
> "it gave up the chance for a free Companion, another Exhaust trigger, more Charge, and an additional memory" (fight 4, item 2)
> "I shifted toward using Muster to convert a slow setup card into immediate Companion and Charge value." (fight 4, item 5)
> "I ... chose To the Front! intending to turn the slow Before Sun and Moon power into an immediate discounted Companion while keeping one energy for Water's Edge." (fight 4, item 1)

I count this one, on the record's explicit "an additional memory," but I flag that the turn sentence alone would be the weakest of the five.

**Count of qualifying turns: 5. Musters among them: 2 (`turn-014`, `turn-058`).**

Turns I considered and **did not** count, so the strictness is auditable:

- `turn-037` (`play "Kurage's Oath"`): "Playing the power now lets the queued Gorou replay generate Block next turn" — and `turn-053`: "The queued free replay will make this power valuable next turn." These read the queue and time a card *around* it, but neither is a Muster nor a deliberate Exhaust; nothing is being put INTO the memory. P3 grades planning *into* the memory. Excluded.
- `turn-063` (`play "Sayu — Yoohoo Art: Fuuin Dash"`): "The free attack consumes the Hydro aura for Swirl, adds damage, and **Exhausts to increase Charge**." Charge only, no memory consequence stated. Excluded under the slot's own distinction.
- `turn-016` / `turn-017` and `turn-060` / `turn-061`, the Muster selection and confirm screens: the sacrifice is chosen for being useless — "Coral Guard has already become unnecessary this turn"; "The power is too slow for the nearly finished fight" — with no memory consequence stated at the moment of choosing. Excluded. This matters and I return to it in §3.

Rule 1 comprehension, stated retrospectively rather than at a graded turn, from the run record item 5:
> "I would also be cautious with Before Sun and Moon: it was slow when drawn, and **transforming it created a 3-Charge memory at the front of the queue that blocked free memories behind it**."

That is exactly Rule 1 — the sacrificed card entered, at 3× cost, at the front — read correctly off the run. The wire confirms it as fact: snapshots 029–032 show `Before Sun and Moon @3` front and **BLOCKED**, with `Sayu @0` stuck behind it.

## 2. Against the threshold

The threshold as written: **at least 3 of 10 graded turns** carry such a plan, **and at least one of them is a Muster**. Falsifier: **0**.

- Qualifying turns: **5**. Threshold is 3. Met, with margin, and it would still be met at 4 if `turn-058` were struck for its turn sentence naming only Charge.
- Musters among the qualifiers: **2** (`turn-014`, `turn-058`). Threshold is 1. Met, and still met at 1 if `turn-058` were struck.
- Falsifier at 0: did not fire. The tester played toward the queue repeatedly and in two different ways.

On the denominator: the run's answered turns run to 66, of which roughly thirty are in-fight plays — comfortably more than ten, so the "of 10" denominator is not short-changed by a truncated run (`termination: max_actions`). I have counted qualifying turns absolutely, which is the strict reading; no plausible selection of ten graded turns from this record drops the count below 3, since the five qualifiers are spread across three separate fights (fight 1: 014, 018; fight 3: 036; fight 4: 052, 058).

The distinction the slot draws is honoured: every counted turn states a consequence in the queue or its Charge, not merely the card's printed body. The three exclusions above are cards played for their bodies or for queue *timing*, and they are excluded.

## 3. Verdict: **PREDICTED**

The threshold is met on its own terms and the falsifier is nowhere near firing. I record one reservation that does not change the verdict, because P3's threshold does not ask for it: the tester's Rule 1 comprehension is **retrospective, not prospective**. At both Muster selection screens (`turn-016`, `turn-060`) the sacrifice was picked for being the most useless card in hand, with no memory reasoning printed; the tester only articulates that the *sacrificed* card is the one that enters, at 3× cost, at the front, in the run record after the fact — and articulates it there as a regret ("blocked free memories behind it"). So the record shows the pattern being *learned across the run* rather than *held before the first Muster*. P3 asks whether the tester plans toward the queue and states the consequence; it does not ask whether the sacrifice-versus-recruit half was priced correctly at the moment of choosing. Graded as written: PREDICTED.

## 4. Judgment: **ADVANCE**

Per the slot's own disposition text, "3 or more says the base kit teaches the pattern and the next question is dose, which is [USER]'s." Five qualifiers across three fights, by both rules, with a correct end-of-run statement of Rule 1's cost and blocking behaviour, supports asking that next question. This is support for advancing the question, not a claim that anything should ship.

The teaching surface is not what I would return here. I note, without proposing a remedy, that the confusions the tester reports repeatedly are elsewhere: the Bake-Kurage **preview** ("its end-of-turn preview changed from granting Block to dealing Hydro damage depending on the latest card played", fight 1; "continued to alternate between copying a card's effect and its printed pulse behavior in a way that was difficult to reconcile", fight 4), Kurage's Oath **timing** ("its 3 Block appeared to remain at the start of round two", fight 3), and a sequencing defect in the harness — the fight-record prompt arriving before the Muster selection and confirmation screens resolved ("the game asked for a fight record before that interaction and the fight itself had actually finished", fight 2; repeated in fight 4). Those belong to slots other than P3 and I do not grade them.
