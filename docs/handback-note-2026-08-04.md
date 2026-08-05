# Hand-Back Note — Next Session Kickoff (Validation Soak + Track B)

Filed verbatim, per the house rule that chat is not a record. Received
2026-08-04 (evening); executed the same evening — the sprint log is
`docs/sprint-track-b-curves-log-2026-08-04.md`, the acceptance it set is
recorded as **R98**.

---

From: [USER] via chat session, 2026-08-04 (evening). For: local Code agent. Context: R88–R97 landed on main (`0691724`), suite 1524 green both modes. The three debts in the final Understudy report are acknowledged and kept verbatim in the record. This note opens the next session with two items, strictly in order. Worktree-per-session (G4). Suite green at boundaries.

Item 1 — The clean N=3 validation soak (opens the session, blocks Item 2's bot feed)

Debt #2 is explicit: no soak has completed a clean N=3 on current code — the last two harness fixes landed after the final soak ran. Until that happens, P1 is working but NOT validated, and the jank-filter promise is not yet relied upon.

* Run one soak, N=3, current main, read-back seeds, no other changes.
* Clean completion → mark P1 VALIDATED in the ledger and delete debt #2.
* Any new harness defect → fix, add the regression test, re-run. The traversal layer is the known expensive half (debt #1) — estimate accordingly and do not call P1.5/Phase-3 numbers until asked.
* Non-goal: no policy changes in this soak. One variable per window — this run validates the harness, nothing else.

Item 2 — Track B kickoff: two feeds, not one

Debt #3 (bots die in Act 1) caps the BOT feed, not telemetry itself. Track B starts now on two feeds:

1. Bot feed: Act 1 curves from validated soaks — dense and cheap.
2. Human feed: the same telemetry hook recording [USER]'s real co-op sessions, which reach Act 3. Sparse, arrives on the table's schedule. Build the hook so a normal co-op session writes the same JSONL schema the soak writes, tagged by feed + seat count. Cross-session note before the schema is shared, if not already covered by P1's.

Deliverables, in order:

* B1 (demand curve), Act 1 first: expected incoming damage and required output per turn, per fight class, from both feeds. Act 2/3 columns fill in as human-feed data arrives; empty cells stay empty and labeled — never extrapolated.
* B2 (output curves): archetype expected damage/block per turn overlaid on B1. Diagnostic surface, never an acceptance target (R14).

Pre-registrations carried in from R89/R95 — grade against B1/B2 when the data supports them, not before:

* Fanfare shape (early half): in Act 1, Fanfare archetype output in fight-turns 1–3 falls short of the demand curve where Salon does not. Instrument: B2 vs B1, bot feed suffices. The late-game half of the Fanfare claim WAITS for Act 3 human-feed data — do not grade it early.
* Salon fill time: turn the Salon first reaches cap; fraction of fight-turns at cap. Instrument: telemetry counters, bot feed suffices. This number decides whether bounded-meter readers get their scaling tag revisited (R95 amendment).

Non-goals for Item 2: no balance values move; no card changes; no floors change; no B3 axis disposition yet (that wants fuller curves); nothing reads drafter prices. Reaction events ride the telemetry schema if the field is cheap to add now (per the promotion path) — measurement only, no reaction constant is touched.

Standing reminders

* Guardrail 7 discipline extends to Track B outputs: bot-derived curves are bot-limited floors; label every chart with its feed.
* Stop-and-surface: any harness defect class OUTSIDE the traversal layer (that would be new information); any schema question the cross-session notes don't already answer; anything that would touch a [USER] gate.
* [USER] is playing Genshin and is not blocking anything. Batch any gate items for one sitting rather than surfacing them one at a time.
