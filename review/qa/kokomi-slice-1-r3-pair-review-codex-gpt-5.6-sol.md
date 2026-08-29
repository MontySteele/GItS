# Kokomi slice 1, round 3 — the pair read, by the independent seat (2026-08-28)

> Subjective feedback from an independent frontier model reading the real
> forms — useful for iteration; not human validation, balance evidence, or
> approval (R217 G). Reviewer: OpenAI `gpt-5.6-sol` via `understudy/seat.py
> review` (ChatGPT-plan sign-in, read-only, everything inline — the prompt was
> the eleven round-3 packets, all eleven forms and verdicts verbatim, and the
> live REPLAY post-state beside each one, sha256
> `c2466b75e85f5ad34e4dde00d40246dfed43d781223999cdcd21c6f3a189dc87`, kept at
> `review/qa/kokomi-slice-1-r3-review-prompt.txt`). The seat's outcome per arm
> is what R217 A lets it decide: RETURN or ADVANCE, never ship. Text below is
> the model's reply, unedited.
>
> **No correction is attached this round**, and that is the round's result as
> much as anything below. Round 2's read carried one: the reviewer and four of
> eleven graders read a 9-damage card as 13 because its face stated the Charge
> rider twice (`EB-164`). The face is fixed, the replay step was added to catch
> exactly that class at grade time, and **every replay that completed confirmed
> the grader's arithmetic to the hit point** — including the two that a reader
> would doubt (a 21-damage line leaving Seapunk on 1, and an attacker taking
> ZERO HP damage through Block). No form was flagged `misread`.
>
> **Three replays are INCOMPLETE and the reviewer was told so:** `t02`, `t04`
> and `t10`, each because the graded line passes through a modal card-selection
> or mode-choice prompt that `staged_turn execute` cannot answer. Those three
> forms are untested, not contradicted, and the gap is filed as `EB-170`.

The round supports four ADVANCE judgments and three RETURN judgments. None warrants ESCALATE: every completed replay confirms the form, and the three incomplete replays are mechanically untested rather than contradictory.

### t02 — Tidal Barrage, whole-turn Exhaust count: ADVANCE

1. **Card involvement:** Played. The grader chose “Gorou … then Tidal Barrage … while Exhausting Send the Runner, then Coral Guard.”
2. **Change in kind of choice:** Yes. In the shipped half, Pearl Barrage appeared only in the offensive alternative: “23 damage but no Block.” The prototype instead entered the chosen defensive line because Gorou’s earlier Exhaust contributes to Tidal Barrage. The turn became a sequencing/resource-conversion choice inside the defended line, not simply Pearl offense versus no-Pearl defense.
3. **Did the cost bind?** Yes, regarding defence: Coral Guard consumed the remaining energy and “gave up 9 damage in exchange for 5 Block.” The counting-basis change itself also mattered by rewarding the prior Gorou Exhaust.
4. **Text problem?** No. The grader correctly treated “per card Exhausted this turn, including the one above” as including both Gorou and the card exhausted by Tidal Barrage. Replay is incomplete because of the selection prompt, so this remains unconfirmed mechanically.
5. **Judgment:** **ADVANCE.** The prototype was played and changed how Exhaust sequencing participates in the attack/defence decision.

### t04 — Shinobu, Warding Ring: ADVANCE

1. **Card involvement:** Played in damage mode.
2. **Change in kind of choice:** Clear change. Shipped Sanctifying Ring killed both Leaf Slimes and gained the four Block simultaneously, producing an intent-insensitive refusal. Warding Ring forced the grader to choose the kills over defence: it “gave up the 4 Block mode” and accepted the Twig Slime’s four damage.
3. **Did the cost bind?** Yes. Taking four Block would give up the damage mode and therefore both 3-HP Leaf Slime defeats. That is a concrete defensive price.
4. **Text problem?** No. The slightly awkward combination of “Gain 4 Block, applying no element” followed by “Applies Electro” did not confuse the grader; Electro was associated with the damage mode.
5. **Judgment:** **ADVANCE.** It directly removes the shipped card’s subsidized defence and makes enemy intent capable of changing the mode. Replay remains untested because of the modal prompt.

### t05 — Shinobu, Sanctifying Circle: RETURN

1. **Card involvement:** Played as the entire turn.
2. **Change in kind of choice:** Not enough. The increased cost removed the shipped half’s follow-up attack, but the same bundled action still killed both status enemies and fully answered the attack. The grader explicitly said its Block was useful “without costing those removals” and again refused the turn as intent-insensitive.
3. **Did the cost bind?** It bound economically but not as a meaningful defence decision. Spending all three energy gave up “the possibility of using the stronger single-target hits against Twig Slime,” but paying for Block did not compete with the card’s decisive two-enemy removal.
4. **Text problem?** No. The potentially surprising statement that the Twig Slime took no HP damage was exactly confirmed: its Block fell from six to three.
5. **Judgment:** **RETURN.** The extra energy costs follow-up damage, but the board still makes the attack-plus-Block bundle dominant for reasons independent of intent. The card or board needs rework.

### t07 — Thoma, Blazing Ooyoroi: RETURN

1. **Card involvement:** Not played, but seriously weighed in Block mode: Block plus All Streams for nine damage.
2. **Change in kind of choice:** It changed the comparison, but unhelpfully on this board. Shipped Thoma offered 17 damage plus three Block against the chosen 21 damage. The prototype’s defensive alternative offered only nine damage plus three Block, widening the offensive sacrifice from four damage to twelve. The grader consequently chose the same three attacks and became intent-insensitive.
3. **Did the cost bind?** Yes, strongly: the form says the chosen line gave up three Block “in exchange for dealing 12 more damage.” The defensive mode’s price was concrete but apparently too steep for the shown 11 attack.
4. **Text problem?** No. The grader separated damage mode, Block mode, and elemental application correctly.
5. **Judgment:** **RETURN.** The card was weighed, but this board only shows the Block mode losing badly and produces no intent-sensitive evidence. A stronger or more discriminating board is needed.

### t08 — Thoma, Crimson Guard: ADVANCE

1. **Card involvement:** Seriously weighed as the alternative.
2. **Change in kind of choice:** Yes. Shipped Thoma could combine with All Streams for 17 damage and three Block, only four damage behind the chosen line. At cost three, Crimson Guard monopolizes the turn: eight damage plus three Block versus 21 damage without Block.
3. **Did the cost bind?** Unambiguously. The grader named a 13-damage price for the three Block and three HP saved.
4. **Text problem?** No. The completed replay confirms the chosen 21-damage line. The grader’s lethal threshold is also arithmetically sound: at 22 HP, a 22-damage attack is lethal without Block but not with three Block.
5. **Judgment:** **ADVANCE.** Pricing Block into the cost line created a large, explicit offence-for-defence exchange that the grader said could reverse under another intent.

### t10 — Itto, Oni Rush: ADVANCE

1. **Card involvement:** Played in damage mode; Block mode was seriously considered.
2. **Change in kind of choice:** Strong change. Shipped Itto produced 23 damage and six Block together and was intent-insensitive. Oni Rush produced the same 23-damage sequence only by choosing damage mode and “giving up preventing the incoming 4 damage.”
3. **Did the cost bind?** Yes. Defence costs the 14-damage mode; offence costs four HP on this board. The grader identified both sides explicitly.
4. **Text problem?** No. The mode distinction and damage arithmetic were understood. Replay is incomplete solely because the tool cannot answer the mode prompt.
5. **Judgment:** **ADVANCE.** This is the cleanest direct conversion of subsidized defence into an explicit mode decision.

### t11 — Itto, Superlative Guard: ADVANCE

1. **Card involvement:** Seriously weighed as the alternative.
2. **Change in kind of choice:** Yes. Shipped Itto plus All Streams dealt 23 and gained six Block simultaneously. At cost three, Superlative Guard instead competes with the 21-damage three-card line: 14 damage plus six Block versus 21 damage and no Block.
3. **Did the cost bind?** Yes. The grader paid seven damage and a worse enemy post-state—10 HP rather than three—to obtain enough Block to prevent all four incoming damage.
4. **Text problem?** No. The replay confirms the chosen line at exactly 21 damage and zero Block.
5. **Judgment:** **ADVANCE.** The higher cost makes defence consume the entire turn and creates a concrete, intent-sensitive seven-damage trade.

| Prototype | Arm | Outcome | Reason |
|---|---:|---|---|
| t02 Tidal Barrage | 1 | **ADVANCE** | Played; whole-turn counting moved the scaling attack into the defended line, while Coral Guard explicitly cost nine damage. |
| t04 Warding Ring | 2 | **ADVANCE** | Played in damage mode; unlike shipped, killing both Leaf Slimes required giving up four Block and taking the attack. |
| t05 Sanctifying Circle | 3 | **RETURN** | Played, but the bundled AOE removal plus Block remained intent-insensitive; the extra cost removed only a follow-up. |
| t07 Blazing Ooyoroi | 2 | **RETURN** | Seriously weighed, but Block mode sacrificed twelve damage for three Block and never became competitive on this board. |
| t08 Crimson Guard | 3 | **ADVANCE** | Seriously weighed; pricing Block into the cost line created an explicit 13-damage defensive price. |
| t10 Oni Rush | 2 | **ADVANCE** | Played in damage mode; the prototype forced a clean choice between 14 damage and six Block. |
| t11 Superlative Guard | 3 | **ADVANCE** | Seriously weighed; paying for six Block cost seven damage and the entire three-energy turn. |

Overall, mutually exclusive modes work on the Shinobu and Itto boards but need a better Thoma test. Cost-line pricing works for Thoma and Itto, while Shinobu’s multi-enemy removal remains strong enough to carry the Block without an intent-dependent decision.