# Kokomi "Kurage memory" — the independent seat's doctrine review, verbatim

**2026-08-29.** The repo-visible doctrine seat, run under the clause-only
protocol (`docs/current/OPERATIONS.md`, "Doctrine seat protocol") on
`review/active/kokomi-kurage-memory-2026-08-29.md` as committed at `531918d`.

Everything below the provenance block is the seat's own words, **unedited**. I
have not argued with a verdict and I have not corrected a fact inside it.

---

## Provenance

**Seat:** `understudy/seat.py`'s repo-visible review door — OpenAI Codex CLI
`0.150.1`, logged in through [USER]'s ChatGPT subscription, model
**`gpt-5.6-sol`**. Independent by model family (R217 C): Claude authored the
proposal, GPT reviews it. NOT blind — this seat is meant to read doctrine.

**Exact command:**

```
python -m understudy.seat review review/qa/kokomi-kurage-memory-review-prompt.txt     --model gpt-5.6-sol --out understudy/logs/seat/kurage-memory-doctrine.md
```

which `understudy/seat.py::review_argv` builds as `codex exec -C <repo>
--sandbox read-only --ignore-user-config --ephemeral --color never -o <out>
-m gpt-5.6-sol -`, with the prompt on stdin.

**The prompt is inlined, not fetched.** `review/qa/kokomi-kurage-memory-review-prompt.txt`,
sha256 `f634d108a796e0bbd8c2c58e3491eb636104cfa39ad3a96aed5e547c4d8dc3f4`,
166225 bytes. The Windows command policy rejects every file
read this seat attempts (recorded when it happened, on the Klee slice-1
doctrine review), so the prompt pastes verbatim and unsummarised: the whole
proposal, LAW's "Character identity — Kokomi", LAW's D1–D9 charter, LAW's
card-sheet rules, the kickoff charter §1–§3, and the whole of
`docs/kokomi-cards.yaml`. One run, no retries, no follow-up round.

**Clause-only compliance: clean.** The seat was told it may not supply card
text, a number, a mode or a rewritten row, and it supplied none. **It
volunteered no remedy**, so there is nothing here to mark DISCARDED, and its
model family stays eligible to grade this row later (`EB-190`).

---

## The seat's reply, verbatim

E1 — THE QUEUE

1. DOES IT ADDRESS THE NOTED ISSUES? — PARTLY. It directly gives Companions a second identity beyond “boring bodies” and makes their play order consequential. It indirectly adds a decision around Charge, but does not by itself separate defence from advancement or let the player decide when Charge converts.

2. DOCTRINE: FOLLOWS — D2, “Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing.” Choosing which Companion enters the visible queue and when is player-steered acquisition and ordering, provided the queued face and downstream target are forecastable under D4.

3. RISK. An automatically replayed Companion may itself satisfy “When Kokomi plays a Companion card,” append another copy, and prevent the queue from shrinking. The proposal does not specify whether remembered plays can remember themselves. It also does not settle whether copied temporary properties remain meaningful or create inherited-effect loops.

E2 — THE FUEL

1. DOES IT ADDRESS THE NOTED ISSUES? — YES for defence feeding the finisher: Companion defence no longer also supplies Charge. PARTLY overall: Charge generation still culminates automatically, and making Companions interesting comes primarily from E1 rather than this exclusion.

2. DOCTRINE: REQUIRES_MODIFICATION — the rotation/accrual law and starter relic must move. The LAW rotation bullet says, “Kokomi only Exhausts her own cards,” while the kickoff §2.1 says accrual “includes Commander-consumed conscripts,” §2.3 says Conscript “feeds Charge on consumption,” and §2.5 prints, “Whenever one of your cards is Exhausted, gain 1 Charge.” The shipped relic likewise says, “Whenever a card is Exhausted, gain 1 Charge and N Burst Energy.” These are additional required amendments beyond R80, not merely implementation details.

3. RISK. “Kokomi’s own non-Companion cards” is not fully aligned with the existing ownership vocabulary: the LAW presently treats conscripted Companions as self-sourced kit for `SUPPORT_CARRY`, while the proposal excludes them for Charge. Without a visible, single definition of “own” versus “Companion,” D4’s prohibition on “invisible feeds” is exposed.

E3 — THE THRESHOLD

1. DOES IT ADDRESS THE NOTED ISSUES? — PARTLY. Spending makes Charge cyclical instead of a number watched forever, and replaying queued Companions gives them consequential afterlife. The conversion itself remains compulsory, so the player still waits for the clock once queue order has been established.

2. DOCTRINE: REQUIRES_MODIFICATION — R80 and the governing Charge bullet must move. R80 says, “CHARGE IS NEVER SPENT. Read or thresholded, never expended,” and the LAW says, “Charge is never spent — uncapped, read but never consumed.” This is one of the expected human-owner amendments. The kickoff §2.1 property, “uncapped; never expended; read (not consumed) by finisher effects,” and §2.2’s Charge-reading finisher charter must move as well.

3. RISK. Threshold firing is underspecified when the queue is empty, targeting is unresolved, and the replay may recursively requeue itself. Those are outcome-defining semantics, so D4 cannot finally pass while they remain open: “At the decision point the player can perceive and forecast the consequences that matter.”

E4 — THE PULSE

1. DOES IT ADDRESS THE NOTED ISSUES? — PARTLY. It breaks the direct defence-to-ever-larger-finisher loop and makes sequencing card types matter. It does not itself improve Companions, and its automatic payoff can still become “play the desired type last, then watch” if the branches do not create materially different choices.

2. DOCTRINE: REQUIRES_MODIFICATION — the kickoff identity and finisher clauses, plus affected printed sheet rules, must move. The identity says, “Kokomi converts card economy into damage”; §2.2 requires finisher shapes that “read Charge”; `bake_kurage` currently promises a pulse of “KURAGE_PULSE_BASE + Charge x KURAGE_PULSE_PER_CHARGE”; `before_sun_and_moon` has the “SOLE EFFECT: +1 to the Kurage pulse MULTIPLIER”; and `kurages_oath` is pinned to the shipped pulse frequency. Persistence also conflicts with Tamakushi Casket’s recorded rule that casting the Burst “REFRESHES a fielded Bake-Kurage.” More than R80 and the relic must therefore move.

3. RISK. The proposal does not define whether the jellyfish’s turn-start replay becomes “the last card Kokomi played,” potentially determining or overwriting the pulse before the player acts. It also leaves the Power branch open, so the pulse’s legality under D2 and D4 cannot be finally judged.

E5 — THE UI

1. DOES IT ADDRESS THE NOTED ISSUES? — PARTLY. It directly makes the Charge clock and Companion queue legible, supporting earlier steering. It does not itself create control, remove defence subsidy, or make Companion bodies mechanically distinct.

2. DOCTRINE: FOLLOWS — D4: “At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule.” The ordered faces, marked threshold, firing indication, pulse indication, and forecast target are the appropriate doctrinal surface, contingent on unresolved targeting and pulse semantics being displayed.

3. RISK. An uncapped horizontal queue can cease to be readable, especially when repeated faces differ by upgrade or temporary properties. The proposal also promises “Everything that will fire next turn is readable this turn,” but start-of-turn Charge changes, self-requeue, or an auto-play changing the pulse can make that claim false.

OVERALL

A. PARTLY. The proposal substantially addresses boring Companions and removes Companion defence as Charge fuel. It replaces passive permanent scaling with an ordered tempo clock, but does not fully resolve “waiting rather than deciding” because firing, payment, and card selection remain automatic.

B. REQUIRES_MODIFICATION. The complete clause set that must move is: the LAW Charge bullet, “Charge is never spent”; R80, “CHARGE IS NEVER SPENT”; the LAW rotation/accrual definition insofar as Companions currently count as her own cards; kickoff §1’s decision loop, “Every card kept is engine; every card burned is Charge”; kickoff §2.1’s universal accrual and “never expended” properties; kickoff §2.2’s Charge-reading finisher requirement; kickoff §2.3’s “feeds Charge on consumption”; kickoff §2.4’s “Each proc is an Exhaust event → Charge” where ownership exclusions apply; kickoff §2.5 and the shipped starter relic text; and the printed rules for `bake_kurage`, `before_sun_and_moon`, `kurages_oath`, `ceremonial_garment`, `nereids_ascension`, `all_streams_flow`, `read_the_current`, `gyorin_formation`, plus Tamakushi Casket’s refresh link. R80 and the relic are indeed expected human-owner amendments, but they are not the only clauses that must move.

C. A visible ordered queue can satisfy D2 even though execution is automatic, because D2 does not require control at execution; it requires that the automatic engine “feed a decision the player can steer,” and play order supplies timing/acquisition steering. D4 is also measured “At the decision point,” which here is the earlier Companion play. This passes only if that point exposes the remembered face, firing conditions, target, recursion rule, and relevant pulse consequence. Visibility alone does not rescue an outcome whose consequential semantics remain unresolved.

D. The proposal is internally inconsistent with doctrine when it claims, “R80 and the relic text are the two amendments this design needs.” The pasted law also binds universal Companion accrual, Charge-reading finishers, the Commander consumption link, the kickoff decision loop, summon duration/refresh, and several printed reader and pulse rules. It also calls the queue “self-bounding” because “every fire removes one,” while its stated trigger can cause an auto-played Companion to append a replacement copy; the proposal contains no exclusion supporting that claim.
