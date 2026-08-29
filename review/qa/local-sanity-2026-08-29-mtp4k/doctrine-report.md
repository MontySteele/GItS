# Local doctrine read -- kokomi-kurage-memory-review-prompt.txt

WHAT THIS IS. A local model re-read turns that are already CLOSED, and its reading is printed beside the two that are recorded. It is SUBJECTIVE FEEDBACK about the READER.

WHAT THIS IS NOT. Not human validation. Not balance evidence. Not a grade: nothing here enters a record, a register or the ledger, and the `local` family is not an approved doctrine seat. Agreement with a recorded reading says the local model was worth reading on these turns; it says nothing about whether any turn is fun.

- prompt: `C:\Users\Monty\Documents\GitHub\GItS-sanity\review\qa\kokomi-kurage-memory-review-prompt.txt` (46985 est. tok)
- model: C:\models\qwen3.8-27b\Qwen3.8-27B-UD-Q4_K_XL.gguf, temperature 0.0
- wall 73.3s, 5739 completion token(s)

## Verdict and clauses, local

- 2. FOLLOWS. Clause D2: “Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing.” The queue is steered by which Companion is played and when, so the queue itself is a decision surface rather than a passive accumulator.
- 2. REQUIRES_MODIFICATION. Clause: the starter relic’s printed text: “Whenever a card is Exhausted, gain Charge and N Burst Energy.” That sentence still says every Exhaust pays Charge, so a rule that Companions pay none cannot stand unless that printed clause moves. I agree this is one of the two expected owner-side amendments.
- 2. REQUIRES_MODIFICATION. Clause R80: “CHARGE IS NEVER SPENT.” A threshold that reduces Charge by a fixed amount is a spend, so this element cannot be legal under the shipped standing law as written. I agree this is the second expected owner-side amendment.
- 2. FOLLOWS. Clause D2: “Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing.” The pulse is still automatic, but its branch is steered by the type of the last card played, so the engine feeds a decision the player can make before the pulse fires.
- 2. FOLLOWS. Clause D4: “At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule — not necessarily verbatim on every face.” The strip is exactly the kind of persistent UI element D4 allows for making the automatic engine forecastable.
- B. REQUIRES_MODIFICATION. The complete list of clauses that must move for this to be legal is:

## Verdict and clauses, recorded GPT read

source: `kokomi-kurage-memory-doctrine-review-codex-gpt-5.6-sol.md`

- 2. DOCTRINE: FOLLOWS — D2, “Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing.” Choosing which Companion enters the visible queue and when is player-steered acquisition and ordering, provided the queued face and downstream target are forecastable under D4.
- 2. DOCTRINE: REQUIRES_MODIFICATION — the rotation/accrual law and starter relic must move. The LAW rotation bullet says, “Kokomi only Exhausts her own cards,” while the kickoff §2.1 says accrual “includes Commander-consumed conscripts,” §2.3 says Conscript “feeds Charge on consumption,” and §2.5 prints, “Whenever one of your cards is Exhausted, gain 1 Charge.” The shipped relic likewise says, “Whenever a card is Exhausted, gain 1 Charge and N Burst Energy.” These are additional required amendments beyond R80, not merely implementation details.
- 2. DOCTRINE: REQUIRES_MODIFICATION — R80 and the governing Charge bullet must move. R80 says, “CHARGE IS NEVER SPENT. Read or thresholded, never expended,” and the LAW says, “Charge is never spent — uncapped, read but never consumed.” This is one of the expected human-owner amendments. The kickoff §2.1 property, “uncapped; never expended; read (not consumed) by finisher effects,” and §2.2’s Charge-reading finisher charter must move as well.
- 2. DOCTRINE: REQUIRES_MODIFICATION — the kickoff identity and finisher clauses, plus affected printed sheet rules, must move. The identity says, “Kokomi converts card economy into damage”; §2.2 requires finisher shapes that “read Charge”; `bake_kurage` currently promises a pulse of “KURAGE_PULSE_BASE + Charge x KURAGE_PULSE_PER_CHARGE”; `before_sun_and_moon` has the “SOLE EFFECT: +1 to the Kurage pulse MULTIPLIER”; and `kurages_oath` is pinned to the shipped pulse frequency. Persistence also conflicts with Tamakushi Casket’s recorded rule that casting the Burst “REFRESHES a fielded Bake-Kurage.” More than R80 and the relic must therefore move.
- 2. DOCTRINE: FOLLOWS — D4: “At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule.” The ordered faces, marked threshold, firing indication, pulse indication, and forecast target are the appropriate doctrinal surface, contingent on unresolved targeting and pulse semantics being displayed.
- B. REQUIRES_MODIFICATION. The complete clause set that must move is: the LAW Charge bullet, “Charge is never spent”; R80, “CHARGE IS NEVER SPENT”; the LAW rotation/accrual definition insofar as Companions currently count as her own cards; kickoff §1’s decision loop, “Every card kept is engine; every card burned is Charge”; kickoff §2.1’s universal accrual and “never expended” properties; kickoff §2.2’s Charge-reading finisher requirement; kickoff §2.3’s “feeds Charge on consumption”; kickoff §2.4’s “Each proc is an Exhaust event → Charge” where ownership exclusions apply; kickoff §2.5 and the shipped starter relic text; and the printed rules for `bake_kurage`, `before_sun_and_moon`, `kurages_oath`, `ceremonial_garment`, `nereids_ascension`, `all_streams_flow`, `read_the_current`, `gyorin_formation`, plus Tamakushi Casket’s refresh link. R80 and the relic are indeed expected human-owner amendments, but they are not the only clauses that must move.

## Diff of the verdict words

- local said: FOLLOWS, REQUIRES_MODIFICATION
- recorded said: FOLLOWS, REQUIRES_MODIFICATION
- same verdict vocabulary: yes
