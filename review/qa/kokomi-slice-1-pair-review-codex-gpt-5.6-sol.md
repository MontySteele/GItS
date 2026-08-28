# Kokomi slice 1 — the pair read, by the independent seat (2026-08-28)

> Subjective feedback from an independent frontier model reading the real
> forms — useful for iteration; not human validation, balance evidence, or
> approval (R217 G). Reviewer: OpenAI `gpt-5.6-sol` via `understudy/seat.py
> review` (ChatGPT-plan sign-in, read-only, everything inline — the prompt
> was the eleven packets and all twenty-two forms verbatim, sha256
> `286c4d94c92502c2cd321f5132e4bb46e376e61b02f7f841068d40c9fb875daf`). The seat's outcome per arm is what R217 A lets it decide:
> RETURN or advance, never ship. Text below is the model's reply, unedited.

# Independent review

## Group A — Tidal Barrage (whole-turn count)

1. **Card exposure:** Yes. Both graders played Tidal Barrage in the lethal line. Opus explicitly relied on “two cards Exhausted this turn,” then Send the Runner exhausting a third, before playing Barrage. GPT likewise used it to “secure lethal damage.” Pearl Barrage, by contrast, was only weighed and rejected by Opus because “the printed scale rate is unstated.”

2. **Kind of choice:** Partly changed, but the board collapses it into lethal versus turtle. Tidal Barrage introduced sequencing and resource-conversion decisions—whether to exhaust Coral Guards and Gorou cards to amplify the attack—but the named alternative remained the same “full turtle” already present on the shipped board.

3. **Did the cost bind?** Yes. Fueling Barrage consumed defensive and future resources. GPT named “the defensive value of two Coral Guards” and “the option to retain those cards”; Opus described a line that “burns both Gorou permanently” and throws away a Coral Guard. Those costs would be felt if lethal failed. However, confirmed lethal makes them largely academic on this board.

4. **Text issue:** Material ambiguity. Opus had to calculate both “14, and 17 if its own Exhaust counts toward its own total.” The text does not establish whether the card it exhausts contributes to its own “cards Exhausted this turn” count. Pearl Barrage was worse: “Scales with the total cost” gives no scale rate.

**Grader disagreement:** They chose effectively the same lethal line, but GPT correctly answered that a different intent would not matter because “the enemy dies before its intent resolves.” Opus answered yes while admitting “the intent barely mattered for the kill itself,” then changed enemy HP in its hypothetical; that does not answer the same-board intent question.

**Outcome: RETURN.** Raise Nibbit’s HP enough that Tidal Barrage cannot guarantee lethal, while keeping its exhaust scaling relevant. The current board proves that the scaling can create lethal, but not that it sustains a live choice sensitive to intent.

---

## Group B

### Either arm — Shinobu: Warding Ring

1. **Card exposure:** No. Neither grader played Warding Ring or seriously weighed it in Q2. Opus mentioned its Block mode only in a hypothetical different-intent answer.

2. **Kind of choice:** No demonstrated change. Both prototype forms repeated the shipped board’s existing Nereid’s Ascension plus damage versus Ascension plus Coral Guard decision. GPT’s alternative was exactly “trading damage … for enough Block,” with Warding Ring absent.

3. **Did the cost bind?** No. Choosing between Warding Ring’s halves never occurred; the card was simply outclassed and ignored.

4. **Text issue:** No grader explicitly tripped. Potentially unclear scope remains in “Choose one: … | Gain 4 Block. Applies Electro”: it is not explicit whether Electro applies after either mode or only the damage mode.

**Grader disagreement:** None that matters; both ignored the test card.

**Outcome: RETURN.** Change the board so Warding Ring itself controls a threshold—ideally where its 3 AoE damage kills or sets up multiple enemies, while its 4 Block answers meaningful surviving damage. Nereid’s Ascension currently decides the board before Shinobu matters.

### Priced arm — Shinobu: Sanctifying Circle

1. **Card exposure:** No. Neither grader played it or named it as the serious alternative. Opus only said it might be considered against a hypothetical attack of “15 or more.”

2. **Kind of choice:** No. The actual choice remained Ascension plus offense versus Ascension plus Coral Guard, exactly as in shipped.

3. **Did the cost bind?** Only as exclusion. At 3 energy, Sanctifying Circle competes with a line that kills two enemies and heavily damages the third. Neither grader treated spending the whole turn on it as credible.

4. **Text issue:** No confusion about Sanctifying Circle itself was recorded.

**Grader disagreement:** Minor choice of final attack—Opus named Water’s Edge while GPT chose All Streams—but neither disagreement involves the prototype.

**Outcome: RETURN.** Change the board, not merely the price: create AoE thresholds where 3 damage plus 4 Block is a credible full-turn package. On this board, the 3-energy price removes the card from deliberation.

---

## Group C

### Either arm — Thoma: Blazing Ooyoroi

1. **Card exposure:** Weakly, by Opus only. Opus listed “Thoma … on its Block mode” inside the defensive alternative, but did not play it. GPT neither played nor weighed it.

2. **Kind of choice:** No. The prototype still produced the same maximum-damage versus Coral Guard mitigation choice seen in shipped. Its internal choice did not create a distinct trade.

3. **Did the cost bind?** The lost rider would bind if Thoma were used, but it was not competitive: 2 energy for 3 Block is inferior to the available 1-energy Coral Guards, while its 8 damage loses to the surrounding attacks. Thus the cost was nominal in practice.

4. **Text issue:** No grader explicitly stumbled. As with Warding Ring, “Applies Pyro” has unclear scope after the two modes.

**Grader disagreement:** Opus raced for 31 damage; GPT chose 25 damage and 5 Block. That disagreement already existed on the shipped board and does not arise from Thoma.

**Outcome: RETURN.** Change the board or the mode values so both halves are credible. In particular, remove or constrain the Coral Guards that make the 3-Block mode redundant.

### Priced arm — Thoma: Crimson Guard

1. **Card exposure:** Mixed. Opus seriously considered “the Thoma line” and rejected it; GPT ignored the card.

2. **Kind of choice:** No. The live decision remained race versus Coral Guard mitigation, the same choice supplied by the other cards in shipped.

3. **Did the cost bind?** Yes, but punitively rather than productively. Opus found that Thoma “costs exactly my 3 energy” and is “strictly worse on damage … by a wide margin,” while “3 Block … is not a meaningful mitigation.” The extra energy caused exclusion, not a close trade.

4. **Text issue:** None recorded.

**Grader disagreement:** Opus regarded the maximum-damage line as correct; GPT retained one Coral Guard. Only Opus tested Thoma, and even there it was dismissed by direct arithmetic.

**Outcome: RETURN.** Reprice or strengthen the package, or construct a board where 8 damage and 3 Block jointly cross thresholds. At 3 energy here, it is dominated before meaningful deliberation begins.

---

## Group D

### Either arm — Itto: Oni Rush

1. **Card exposure:** Yes. Both graders played Oni Rush in damage mode. Opus also seriously considered “Itto on the Gain 6 Block half plus one Coral Guard.”

2. **Kind of choice:** No. The explicit mode choice sharpened offense versus defense, but that same race-versus-turtle choice was already available from Coral Guard and the shipped Itto. GPT’s alternative did not even use Block mode: it replaced Itto with “Coral Guard and Water’s Edge.”

3. **Did the cost bind?** Yes. Taking damage mode meant accepting the full 8 damage instead of receiving shipped Itto’s free 6 Block. Opus named “8 HP, taken on the chin”; shipped took only 2 after the rider. That is a real, felt cost.

4. **Text issue:** None recorded.

**Grader disagreement:** None on the chosen line. They differed only on the defensive alternative: Opus considered Oni Rush’s Block mode, while GPT preferred other cards.

**Outcome: RETURN.** The card creates a real cost, but not a new kind of choice. Use a board where Oni Rush’s two modes—not Coral Guard—are the pivotal alternatives, perhaps by reducing redundant standalone Block and setting simultaneous 14-damage and 6-Block thresholds.

### Priced arm — Itto: Superlative Guard

1. **Card exposure:** Mixed. Neither played it. Opus explicitly priced it as an alternative—“the whole turn … 20 damage and 6 Block”—while GPT only considered replacing Water’s Edge with Coral Guard.

2. **Kind of choice:** No. The decision remained maximum damage versus partial mitigation from Coral Guard.

3. **Did the cost bind?** Yes, but by making the card unattractive. Opus calculated that it “loses 11 damage to buy 6 Block,” which is a poor exchange against an 8-damage intent. The extra energy is strongly felt, but it generates dominance rather than tension.

4. **Text issue:** None recorded.

**Grader disagreement:** Only Opus seriously tested the priced card; GPT’s alternative bypassed it entirely.

**Outcome: RETURN.** Change the board so the combined 14 damage and 6 Block cross both an offensive and defensive threshold. Here, three efficient 1-cost attacks make the 3-energy package an easy rejection.

## Summary

| Group | Arm | Outcome | One-line reason |
|---|---|---|---|
| A | Tidal Barrage | RETURN | Scaling mattered and consumed resources, but guaranteed lethal made intent and the alternative nonbinding. |
| B | Warding Ring — either | RETURN | Neither grader played or seriously weighed the card. |
| B | Sanctifying Circle — priced | RETURN | The 3-energy card was excluded; Ascension and Coral Guard supplied the entire choice. |
| C | Blazing Ooyoroi — either | RETURN | Its modes were dominated by surrounding attacks and Coral Guards. |
| C | Crimson Guard — priced | RETURN | The added energy bound only by making the package an easy rejection. |
| D | Oni Rush — either | RETURN | Forgoing 6 Block was real, but it reproduced the board’s existing race-versus-turtle choice. |
| D | Superlative Guard — priced | RETURN | The package lost too much damage and was bypassed by cheaper cards. |
