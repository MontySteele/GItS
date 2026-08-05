# S4 Ledger Consistency Audit
**Date:** 2026-08-05 · **Repo:** /home/user/GItS (GItS / Teyvat-Spire) · **Scope:** tier0 + klee-mod DECISIONS (entries 1–93, R39–R97, D2–D5; klee-mod C1-through-Neap-Tide incl. R73–R80), charters, countersign packages, live queues · **STRICTLY READ-ONLY — nothing was amended; every resolution below is PROPOSED, NOT EXECUTED.**

## 1. Summary table

| # | Class | Severity | One-line |
|---|---|---|---|
| F1 | c (fired trigger) | **HIGH** | R87(1)'s Furina deferral trigger fired and its replacement condition dissolved; backlog still says "pending the playtest" |
| F2 | a (live contradiction) | **HIGH** | DRAFTER 13 is simultaneously "the landed world" and "not done"; its acceptance fixture is assigned to the wrong stream and fails today |
| F3 | d (superseded cited as live) | MEDIUM | Principles §4.5 and Furina kickoff §3 still state the pre-R41 Spotlight design as law, unannotated |
| F4 | d | MEDIUM | R84's "only quotable roster table" was archived by the D13 bump; the designation was never amended |
| F5 | b (stale fence) | MEDIUM | Backlog §2 orders the Kokomi stability instrument built; D5 records it built two days earlier |
| F6 | c | MEDIUM | Neap Tide's pre-registered G5 fork waits on "playtest three"; a Kokomi-seat playtest has since run and no doc evaluates the fork |
| F7 | b | MEDIUM | docs/README index rows contradict the R92-era discharge of A-G1 (three rows stale) |
| F8 | d | MEDIUM | Principles §4.7 still asserts "Fontaine designs zero Rare companions," falsified by R64 |
| F9 | c | MEDIUM | R56's [USER] "too strong" flag on `kurages_oath` = 12 is still absent from the playtest protocol that would exercise it |
| F10 | d | LOW | Klee charter cites the retired two-sided spark boss band; law is floors-only since R47 |
| F11 | d | LOW | Kokomi kickoff still declares elite axes A2+A4; R51 ruled A2+A6 |
| F12 | d | LOW | Furina kickoff §4 still lists the dead "Encore gained" Fanfare leg with no fence |
| F13 | d (paper) | LOW | Charter footer still says "402 canon cards" after R92/3a corrected the header |
| F14 | d (paper) | LOW | role-tempo-floors.yaml cites "R91/1c" for a rule recorded as R90/1c |
| F15 | b (paper) | LOW | missed-requirements Tier 5 still lists two sheet comments as stale that were fixed at source |
| F16 | d | LOW | README calls the EPOCH-1 numbers "the current canonical-cell baseline"; they are a D10-world figure, archived twice over |
| F17 | d | LOW | open-playtest-items §2 says Kokomi "has had no table time at all"; three later records say otherwise |

Class e ([USER] gates) are in §3 — 20 queue entries, all double-cited.

---

## 2. Findings, severity-ranked

### F1 — HIGH — class c: the Furina deferral chain fired, then its replacement condition dissolved, and no live doc re-points it
- **Cite A:** `docs/backlog-2026-07-29.md` §3 preamble + items 1–3 (lines 211–238): *"items 1–3 DEFERRED pending the Furina playtest — the question it must answer first is whether the pilot is simply better at Salon…"*; items 1–3 (strength lever + legibility, dead-archetype question, salon leak) stand unstruck. Same standing in `tier0/DECISIONS.md` R87(1) (~line 2843): *"Standing consequence until it runs: no Furina balance value moves, the fanfare STOP holds."*
- **Cite B:** `docs/axis-validity-session-charter.md` §1 (lines 30–53): the playtest **ran and was graded** ("three-seat human co-op playtest… 2026-08-01/02… Verdict: BY CONSTRUCTION"), and the ratified consequence converted the standing to *"waiting on Track A's first lint run… the fanfare STOP holds until the fanfare cells have floors to fill toward."* Then `docs/sprint-axis-validity-track-a-log-2026-08-04.md` §0 (line 18: "**Furina fails nothing at all**") and §7.3 (lines 313–341: *"The fanfare archetype still fails nothing, on repaired floors"*), with R90/1b (`tier0/DECISIONS.md` ~3028) moving the question to Track B.
- **Inconsistency:** the trigger (the playtest) fired; the converted condition (fanfare lint floors to fill toward) can never be met, because the lint found no fanfare floors to fill and the question was ruled out of Track A entirely. The three highest-leverage Furina items and the fanfare STOP now have no recorded governing condition, while the live register still says they wait on a playtest that already happened.
- **PROPOSED (NOT EXECUTED):** amend `docs/backlog-2026-07-29.md` §3 items 1–3 in place (per its own strike-with-reference rule) to record the R87(1) → charter-§1 → R90/1b chain, and state the new condition explicitly (presumably: Track B's output-curve instrument / B-G1). Add a dated cross-reference note under R87(1) in `tier0/DECISIONS.md` pointing at the conversion, in the style of the R29d banner.

### F2 — HIGH — class a: "DRAFTER 13 landed" and "DRAFTER 13 is not done" are both on the books, and the acceptance fixture is mis-assigned
- **Cite A:** `docs/sprint-sim-hygiene-log-2026-07-29.md` Task 1 (lines 6–40, 218): DRAFTER 12 → 13 landed 2026-07-29 (*"World at close: RT7 / D13 / P3 / C4"*, *"op parity OK: 56 registered ops, 56 priced"*), with *"the ledger entry for the repricing is the user's to write, because every number below is PROPOSED."* `tier0/constants.py:917` confirms `DRAFTER_VERSION = 13`.
- **Cite B:** `tier0/DECISIONS.md` R96 item 1 (~lines 3310–3315, countersigned 2026-08-04): The Gallery Stirs' 0.0 offer score is *"almost certainly one of the 42"* zero-priced ops and *"DRAFTER 13 is not done while The Gallery Stirs scores 0.0 at offer."* `docs/backlog-2026-07-29.md` §1 (~lines 93–102) still carries the "drafter prices 42 of the engine's 56 ops at exactly zero" entry **unstruck**, with the 08-04 routed note appended beneath it citing it as live.
- **Inconsistency:** the 42-of-56 op defect was fixed five days before R96 cited it as live (same register, entry never struck). Verified in the current tree: `score_offer` for `crowd_work` ("The Gallery Stirs") returns **0.0 today under the stamped D13** — the zero comes from `_static_power`'s power-name blindness (`tech-debt-audit-2026-07-26.md` §2.5, the still-unopened `_static_power`/EPOCH-2 session), not from the op enumeration D13 repaired. The countersigned acceptance fixture is therefore bound to a stream whose mechanism cannot clear it, while the world stamp says that stream already shipped.
- **PROPOSED (NOT EXECUTED):** strike the backlog §1 op-pricing entry with the sim-hygiene commit reference; re-home the Gallery Stirs fixture from "DRAFTER 13" to the `_static_power` repricing session (where R96 item 2 already sits) via a dated correction note on R96; and write the owed D13 ledger entry (a [USER] gate — see §3, G8).

### F3 — MEDIUM — class d: the Spotlight law text in both law docs describes the retired design
- **Cite A:** `docs/teyvat-spire-design-principles.md` §4.5 (lines 111–114): one Spotlighted **character** per player, selector-designation, *"+50% printed numbers"* baseline, *"Self-Spotlight at a reduced rate is the solo fallback and the primary anti-self-buff lever,"* per-turn cap in schema. Same design at `docs/furina-kickoff-v0.1.md` §3.1–3.2 (lines 57–98), unannotated.
- **Cite B:** `tier0/DECISIONS.md` R41 (lines 816–844, USER ruling 2026-07-22): **CENTER STAGE** — Furina's cards generate Fanfare and *"receive no numeric Spotlight bonus"*; **GUEST CAST** *"designates the Companion category rather than one character."* Confirmed live at `docs/red-pen-2026-07-26.md` R2(a) (lines 91–104), which rules on exactly the two-mode split.
- **Inconsistency:** the constitution and the character charter both state, as current law, a designation model (character-level, self-at-reduced-rate) that USER rulings replaced in July; neither carries the supersession fence the same docs use elsewhere (cf. the G-F1 annotation and the v1.12/v1.13 draft fence). A reader of the law docs alone would design against the dead system.
- **PROPOSED (NOT EXECUTED):** add a v1.14-style DRAFT amendment (or an inline annotation of the G-F1 form) to principles §4.5 and kickoff §3 recording the R41/R2 two-mode design, pending [USER] ratification.

### F4 — MEDIUM — class d: R84's "only quotable roster table" is archived, unamended
- **Cite A:** `tier0/DECISIONS.md` R84 (~2695): *"the fresh 3-act roster table lives in the review doc s7 — the only quotable roster table."* That table is a DRAFTER 12 world (`docs/silent-pilot-review-2026-07-27.md` line 224: *"constants live in tier05/draft.py as DRAFTER_VERSION 11"* / §6 "DRAFTER_VERSION 12").
- **Cite B:** `tier0/DECISIONS.md` R87(3) (~2868): *"on the stamp bump every drafter-layer number taken under DRAFTER 12 becomes archive and must be re-measured before it is quoted again."* The bump landed 2026-07-29 (`docs/sprint-sim-hygiene-log-2026-07-29.md` lines 137–138 even carry the paired D12/D13 roster-anchor stamps).
- **Inconsistency:** R84's standing designation and R87(3)'s archive rule cannot both be followed; a reader chasing "the only quotable roster table" lands on archived numbers, while the actually-current (PROPOSED) D13 anchors sit in the sim-hygiene log with no designation at all.
- **PROPOSED (NOT EXECUTED):** dated cross-reference note on R84 (banner style) marking the s7 table archived by R87(3)'s bump and pointing at the D13 roster-anchor run as the successor pending ratification.

### F5 — MEDIUM — class b: the live register orders an instrument built that the ledger records as built
- **Cite A:** `docs/backlog-2026-07-29.md` §2 (lines 165–169): *"Kokomi stability-band instrument… no variance/flatness metric exists in tier05/run_metrics.py or tier0/harness/metrics.py. Build the instrument and report numbers."* (Restating `docs/missed-requirements.md` §1.3, lines 42–53.)
- **Cite B:** `tier0/DECISIONS.md` D5 (2026-07-27, lines 2504–2515): *"Serenitea Sweep I's E1 built the instrument (`run_metrics.stability_profile`) with band = None and every value reported rather than asserted."* Verified: `tier05/run_metrics.py:236` defines `stability_profile`; `tier05/exp_kokomi_stability.py` exercises it.
- **Inconsistency:** the register entry was stale at its own creation date (07-29 vs 07-27) and remains so; a session picking up backlog §2 would rebuild shipped work. The genuinely open half — the band **declaration** — is correctly tracked separately (backlog §3 item 5, D5 clauses 2–4).
- **PROPOSED (NOT EXECUTED):** strike the backlog §2 instrument entry with a reference to Sweep I / D5, leaving only the declaration gate.

### F6 — MEDIUM — class c: the G5 fork's trigger has plausibly fired, unevaluated
- **Cite A:** `klee-mod/DECISIONS.md`, Neap Tide addendum, *"PRE-REGISTERED FORK for playtest three (G5, confirmed)"* (lines 2348–2369): hands-confirm-weak → lever 2 in an isolated cell; hands-say-fine → lever 3 plus a **logged sim-calibration offset**; *"No lever is pulled before the playtest."*
- **Cite B:** `docs/axis-validity-session-charter.md` §1 (lines 34–36): a three-seat playtest **including Kokomi** ran 2026-08-01/02 on build 0.2-247, and §2 quotes a Kokomi verdict ("machinery fun, card pool iffy"). Meanwhile `docs/kokomi-playtest-protocol.md` "Answers" (lines 196–216) is entirely blank.
- **Inconsistency:** a Kokomi table session has occurred since the fork was registered, and no document evaluates the fork, pulls or declines a lever, or records whether that session counts as "playtest three." The registered payoff of the fine-branch — writing down the exhaust-loop calibration offset "asserted three times and never written down as a number" — remains unwritten either way.
- **PROPOSED (NOT EXECUTED):** a dated note on the Neap Tide addendum (or in the backlog §3 queue) stating whether the 08-01/02 session is the fork's trigger; if yes, the fork evaluation becomes a [USER] sitting item; if no, the fork's trigger should name the protocol playtest explicitly so it cannot fire silently again.

### F7 — MEDIUM — class b: three docs/README index rows contradict the R92-era discharge
- **Cite A:** `docs/README.md` line 40 (charter row): *"A-G1 and B-G1 are still open gates"*; line 65 (`role-tempo-review.tsv`): *"Nothing here has landed on a sheet; [USER] gate A-G1 closes first"*; line 67 (`role-tempo-debt.tsv`): *"Delete it with P1's null."*
- **Cite B:** `docs/axis-validity-session-charter.md` §7 annotation: *"A-G1 DISCHARGED 2026-08-04"*; `docs/sprint-axis-validity-track-a-log-2026-08-04.md` §7.5: *"219 rows, all three sheets, both fields… 135 divergences resolved to zero"* (verified: `tempo_band` appears 82/76/61 times in the three sheets); and `tier0/DECISIONS.md` R90/1a (~3040): *"The debt list is deleted when the reworks address the gaps, not before."*
- **Inconsistency:** the index — the document this audit's own corpus rules designate as the current-vs-archived arbiter — asserts an open gate that is discharged, calls landed tags provisional, and gives the debt file a deletion rule that R90/1a superseded (the "delete with P1's null" wording survives from the pre-countersign §5 of the track log).
- **PROPOSED (NOT EXECUTED):** update the three README rows: charter row → "B-G1 remains open"; review.tsv row → "LANDED 2026-08-04 (R91); kept as the derivation record"; debt.tsv row → R90/1a's deletion rule and the "30 → 19 was not eleven wins" caveat.

### F8 — MEDIUM — class d: the constitution still asserts a falsified roster fact
- **Cite A:** `docs/teyvat-spire-design-principles.md` §4.7 amendment note 1 (lines 128–135): *"Not hypothetical: **Fontaine designs zero Rare companions**, so Furina's home-region slot 1 already widens the nation whenever it rolls a Rare."* (Also `tier0/DECISIONS.md` R59, line 1793: "Fontaine ships ZERO Rare companions today," unannotated.)
- **Cite B:** `tier0/DECISIONS.md` R64 (lines 1922–1937, same day): *"Fontaine's Rare roster goes to four… The banner therefore becomes selective, and is wired… across all three surfaces at once."* (docs/README archive map already flags the sibling claim in the shop-channel log as "stale since 15fc78f.")
- **Inconsistency:** the principles doc — the master law — carries a load-bearing empirical claim (used to justify R59's slot-2 floor) that was falsified by R64 the same day, with no annotation; the sibling stale copy in an *archived* doc got a staleness note while the copy in the *live* law did not.
- **PROPOSED (NOT EXECUTED):** one-line dated annotation in §4.7 note 1 (and optionally on R59): "Fontaine Rares are four since R64; the banner is selective; the zero-Rares brittleness argument is historical context for the floor, not a current fact."

### F9 — MEDIUM — class c: the `kurages_oath` "too strong" flag never reached the instrument that would test it
- **Cite A:** `tier0/DECISIONS.md` R56 (lines 1548–1551): *"RULED at 12, with [USER]'s flag on the record: 'I feel like that's too strong, but we can rebalance later.' First knob back."* `docs/missed-requirements.md` §3.3 (lines 166–174) names the exact gap: absent from the protocol's standing-flags list, *"so the one playtest that could judge it won't be told to look."*
- **Cite B:** `docs/kokomi-playtest-protocol.md` — re-stamped 2026-07-29, standing-flags section (lines ~75–98) covers `KURAGE_PULSE_PER_CHARGE` and `burst_max` only; grep for `kurages_oath` / "oath" returns **zero hits** in the file today.
- **Inconsistency:** the miss was audited on 2026-07-26, the protocol was edited again on 2026-07-29, and the flag was still not added; the only tracking is inside backlog §3 item 9's ratification batch, which is a desk queue, not the table instrument.
- **PROPOSED (NOT EXECUTED):** add `kurages_oath = 12` (with the R56 quote and the "first knob back" disposition) to the protocol's standing-flags list, feeding Q4.

### F10 — LOW — class d: Klee charter cites a retired two-sided band
- **Cite A:** `docs/klee-character-design.md` §4 (line 29): Spark Spray *"boss band 45–65% under plausible drafts"* (ratified pass-3 form).
- **Cite B:** `tier0/DECISIONS.md` R47 (lines 1121–1126): *"Their old upper bands no longer model real drafts; Tier 0.5 owns the upper-power comparison, while the authored batteries retain only their matchup floors."* Verified: `tier0/content/characters/klee.yaml:38–44` now reads `spark_weighted: [0.45, null]` — floors-only.
- **Inconsistency:** the charter states a ceiling (0.65) that is no longer law; a reader tuning spark against the charter would treat a >65% boss cell as a violation the code no longer flags.
- **PROPOSED (NOT EXECUTED):** in-place dated annotation on §4 item 2: "upper bands retired R47; floors-only since the Burst-meter-40 world."

### F11 — LOW — class d: Kokomi kickoff's elite-axis declaration superseded by R51
- **Cite A:** `docs/kokomi-kickoff-v1.md` §3 (line 168): *"Elite-axis declaration (proposed, [USER]-gated): A2 Scaling + A4 Utility."*
- **Cite B:** `tier0/DECISIONS.md` R51 (lines 1287–1291): *"Kokomi's elite pair is A2 Scaling + A6 Utility, replacing the kickoff's 'A2 + A4 Utility' wording — the A4 terminology clash is discharged."*
- **Inconsistency:** the kickoff is archived-verbatim by design, but `docs/README.md` line 39 fences only its *"numeric sections"* as superseded — the elite-axis declaration is not numeric, so the fence does not cover the one identity-level supersession in the doc.
- **PROPOSED (NOT EXECUTED):** widen the README row (or add a header note to the kickoff) to name R51's elite-pair replacement explicitly.

### F12 — LOW — class d: Furina kickoff §4 still lists the dead "Encore gained" Fanfare leg
- **Cite A:** `docs/furina-kickoff-v0.1.md` §4 (lines 113–118): *"Generation is activity-based, never passive: HP lost, **Encore gained**, Encore spent, and… each Spotlighted card played."* The G-F1 annotation beneath it corrects only the uncapper clause.
- **Cite B:** `docs/teyvat-spire-design-principles.md` v1.12 DRAFT (lines 265–288): *"**The 'Encore gained' leg is dead.** Ruled [USER] 2026-07-28… shipped the same day in both engines"*; live set is HP lost / Encore spent / Encore absorbed / Spotlighted play.
- **Inconsistency:** the principles carry a proper DRAFT fence; the kickoff — the doc a Furina designer reads first — states the dead leg with no marker at all.
- **PROPOSED (NOT EXECUTED):** mirror the v1.12 draft note into kickoff §4 (annotation form, ratification riding on v1.12's countersign).

### F13 — LOW — class d (paper): the charter's footer kept the corrected figure
- **Cite A:** `docs/axis-validity-session-charter.md` line 234–235: *"vocabulary review (validated against 402 canon cards)."*
- **Cite B:** `tier0/DECISIONS.md` R92/3a (lines 3145–3149): *"'402 canon cards' was an arithmetic slip… the DLL prints 439, of which 410 are draftable. Header corrected."*
- **Inconsistency:** the header was corrected; the footer instance of the same figure was not.
- **PROPOSED (NOT EXECUTED):** correct the footer line on next touch of the charter (explicitly allowed by R92/3a's "fix on next touch").

### F14 — LOW — class d (paper): floors file cites the wrong R-number
- **Cite A:** `docs/role-tempo-floors.yaml` header (line 8): *"R91/1c: the comparison population is a canon PACKAGE…"*
- **Cite B:** `tier0/DECISIONS.md` — 1c is a clause of **R90** ("1c — the floors are re-derived from canon PACKAGES," ~3036); R91's clauses are 2a–2d.
- **Inconsistency:** a machine-generated header cites a ruling that does not contain the clause; anyone resolving the citation lands on the tag-review ruling instead of the floors ruling.
- **PROPOSED (NOT EXECUTED):** fix the generator string in `tools/canon_role_tempo.py` and regenerate (comment-only change).

### F15 — LOW — class b (paper): missed-requirements still lists two fixed sheet comments as open
- **Cite A:** `docs/missed-requirements.md` Tier 5 (lines 344–348): *"Two stale sheet comments that lints can't catch: `warmup_act` still says '(Crackle parity)'… `docs/mondstadt-companions.yaml:4` still asserts 'Companion cards NEVER scale'."*
- **Cite B:** `docs/furina-cards.yaml:238` now reads *"Was: 3 damage flat, Crackle parity…"* (historical form); `docs/mondstadt-companions.yaml:5–8` carries the G2 correction (*"this line opened 'Companion cards NEVER scale…' — contradicted by USER RULING 1 of 2026-07-21"*).
- **Inconsistency:** both were fixed at source (the file's own ledger-corrections practice) but the Tier-5 entry was never struck the way the five "Ledger corrections" items were.
- **PROPOSED (NOT EXECUTED):** strike the two sub-items in Tier 5 with the correcting references.

### F16 — LOW — class d: README designates an archived baseline as "current"
- **Cite A:** `docs/README.md` line 52: `epoch-1-log-2026-07-26.md` — *"The current canonical-cell baseline lives here."* That baseline is stamped `RT7/D10/P3/C3` (`docs/epoch-1-log-2026-07-26.md`, "New baseline" section).
- **Cite B:** `tier0/DECISIONS.md` R87(3) (~2868–2877) archives all pre-D13 drafter-layer numbers on the bump; `tier0/constants.py:917` shows the bump landed. Fresh D13 anchors exist only in `docs/sprint-sim-hygiene-log-2026-07-29.md` (lines 137–138), PROPOSED.
- **Inconsistency:** "current" points two world-bumps behind the stamp; per R68/R87 discipline those numbers may not be compared against anything measured today.
- **PROPOSED (NOT EXECUTED):** README row → "EPOCH 1's landing record and the D10-world baseline (archived by the D12/D13 bumps); current anchors: sim-hygiene log, PROPOSED."

### F17 — LOW — class d: the live table-agenda doc says Kokomi has never been played
- **Cite A:** `docs/open-playtest-items.md` §2 (line 51): *"She has had no table time at all."* (Header keeps §1–§5 as the still-live table agenda.)
- **Cite B:** `klee-mod/DECISIONS.md` Neap Tide B3 (lines 2303–2314): *"Both playtests are recorded as BASELINE OBSERVATIONS"* (2026-07-26); `tier0/DECISIONS.md` D5 (HP data reviewed in a Kokomi playtest); `docs/axis-validity-session-charter.md` §1 (Kokomi seat, 2026-08-01/02).
- **Inconsistency:** the 07-29 de-drift pass folded five corrections into this file but left the "never played" line, which three later records contradict; a reader would mis-frame the next Kokomi session as a first exposure (which matters because D5 designates the earlier plays as contaminating-exploratory).
- **PROPOSED (NOT EXECUTED):** annotate §2 in place: "played exploratory (2026-07-25/26, D5-designated) and in the 08-01/02 three-seat holdout; the *protocol* playtest (Answers) has not run."

---

## 3. The undischarged [USER] gate queue

> **IDENTIFIER NOTE + STATUS BANNER, added 2026-08-06 by the housekeeping sweep (Track X).** The gates below are minted here and their canonical qualified form is **`S4-G1` … `S4-G20`** — six other namespaces in this repo mint bare `G1`/`G2` (Curtain Call's `CC-G1/G2`, Serenitea Sweep's `SS-G1…G4`, Neap Tide's `NT-G2…G8`, animation sprint 2's `AS2-G1/G2`, Track N's `LF-G1…G5`, Track G's `RA-G1/G2`). Resolver: `docs/registry/identifiers.md` §2.1. **This table is a read-only audit artifact and its State column is NOT amended here** (the report's own "nothing was amended" standing holds). Two rows have since been discharged — **`S4-G1` by R108** and **`S4-G8` by R107(a)** — and `S4-G7` was re-fenced onto `B-G1` by R107/F1. ~~Read the State column below as current.~~ **The live, reconciled queue is `docs/registry/user-queue.md` §2.**

All items explicitly awaiting the user that no later document discharges. Healthy-but-open items are included so the queue is visible in one place.

| # | Gate | Source (cite) | Tracked at | State |
|---|---|---|---|---|
| G1 | **R88 countersign** — Zhongli slot 4 / Itto eligibility record | `tier0/DECISIONS.md` R88 ("DRAFT — needs [USER] countersign") | `backlog-2026-07-29.md` §3 item 9; charter header ("R88 sits in DRAFT… this is the blocker") | OPEN — also the recorded blocker on the Zhongli deep dive |
| G2 | **R89 countersign** — Furina legibility sprint record | `tier0/DECISIONS.md` R89 (DRAFT) | backlog §3 item 9 | OPEN |
| G3 | **v1.12 amendment ratification** (Fanfare single-leg + printed cap/grant X values) | principles "Amendment DRAFTS" (lines 265–307) | backlog §3 item 9 | OPEN; shipped in code, law text unratified |
| G4 | **v1.13 amendment ratification** (bounded runtime art fitting) | principles drafts (lines 308–338) | — (drafts section only) | OPEN |
| G5 | **B-G1 — per-axis disposition of the seven-axis scorecard**; carries the re-registered Fanfare P1 | charter §4/§7; R90/1b | charter §7 annotation ("B-G1 remains deferred") | OPEN — until it rules, axis numbers stay "reportable, not load-bearing" (D3 clause 3) |
| G6 | **Kokomi stability-band declaration** (from design intent, before the confirmatory playtest; may not be revised against it) | `tier0/DECISIONS.md` D5 clauses 2–4 | backlog §3 item 5 | OPEN — gates grading her protocol playtest |
| G7 | **Furina items 1–3** (strength lever + legibility, dead-archetype, salon leak) | R87(1); backlog §3 items 1–3 | see F1 — governing condition currently dangling | OPEN, mis-fenced |
| G8 | **DRAFTER 13 repricing ledger entry / number ratification** | `sprint-sim-hygiene-log-2026-07-29.md` ("the ledger entry… is the user's to write; every number PROPOSED") | not in backlog §3 explicitly | OPEN — see F2 |
| G9 | **Ratification batch** (fanfare-rework X values; conversion clauses; `lasting_impression`; negative-floor semantics; D6 bow space; `kurages_oath`=12 re-file; pulse 2-vs-3; Curtain Call's four follow-ons; `scattering_spray` 7→6; Spotlight ten-icons-vs-family; Klee dead-card reworks §3.4) | backlog §3 item 9 | backlog §3 item 9 | OPEN |
| G10 | **Shop channel §7 close-out**: P1–P3 grading countersign; does the purse ever bind (~220 unspent gold vs "pricing is the governor"); the 1.15× surcharge companions don't collect; Track A pool migration; **R60 phase-2 fantasy-leak grading** ("after phase 1 is live at the table" — it has been, since 2026-07-25) | `tier0/DECISIONS.md` R60/R63; principles §4.7 notes 2–3 | open-playtest §6.2 + missed-requirements Tier 5 (§7.6/§7.7) | OPEN — R60's stated trigger has been satisfied for ~10 days |
| G11 | **R29d — the naming/lore eyes-on pass (Furina)**, "owed before ship, the pass itself is the closure"; plus Kokomi R58 fill block AUTHORED-NOT-AUDITED and kickoff ask 10 (audit pre-C-milestone) | `tier0/DECISIONS.md` entry 75 + R29d banner; R58 | missed-requirements Tier 5; backlog §3 item 9 | OPEN |
| G12 | **R86 gates G1/G2** — contact-sheet eyes-on (four REHUNT picks + `standing_room_only` overturn) and in-game screenshot review of the twelve Curtain Call cards + A0 smoke run | `tier0/DECISIONS.md` R86 ("OPEN, and NOT closed by this entry") | backlog §4 | OPEN |
| G13 | **Neap Tide standing question** — Kokomi below the (Ironclad-anchored) floor; levers: soften G6 (law conflict with R79), give accrual back high-frequency, or re-anchor; plus the G5 fork | `klee-mod/DECISIONS.md` E2/E2b + addendum | see F6 | OPEN — "none is Code's to pull" |
| G14 | **Kokomi protocol playtest** (Q1–Q7; Answers blank) + three priority checks | `kokomi-playtest-protocol.md` | backlog §4 | OPEN — blocked on G6 per backlog |
| G15 | **Corpse detonation settlement** (~10 s at the table; failure invalidates every sim bomb number vs killable enemies) | `klee-mod/DECISIONS.md` "Corpse detonation — OPEN" (2026-07-21) | open-playtest §1 item 2; backlog §4 | OPEN since 2026-07-21, through ≥4 playtests |
| G16 | **G-A5(b) fourth shape** — one capture of a Power play raising the Fanfare floor | `red-pen-2026-07-26.md` Part 3 ("remains OPEN on that one line") | itself | OPEN |
| G17 | **Table looks**: D5 salon capture (sprite-scale fix landed, capture not), B5 motion pass + facing taste, E2 icon picks (4 REHUNT), hover-targets question | open-playtest §3; backlog §4 | backlog §4/§5 | OPEN |
| G18 | **Klee pass-4 ask A3** — 28/21/14 archetype-band deviation vs principles' 15–20, never amended or accepted (ask A5 is *deliberately* deferred by D3, distinct) | missed-requirements Tier 5 (test_klee.py "QUEUED FOR USER" docstring) | missed-requirements only | OPEN |
| G19 | **Sly unification design ruling** (two mechanics, one word — filed by [USER] with ask A4) | `tech-debt-audit-2026-07-26.md` §5 | itself (kept-current §) | OPEN |
| G20 | **Standing Ovation boost expiry ruling**; sim-vs-C# salon RNG divergence acceptance; taste passes (Kokomi 58 faces + 15 companions, L12 duplicate pairs, `kaboom == spark_knight_style`); infra (branch protection / gh); manifest MAJOR bump at next release sprint (R70, dormant by design) | backlog §1 P3-cluster + §5; R70 | backlog | OPEN |

---

## 4. Unconfirmed leads (not double-citable to the standard above)

1. **"Playtest three" numbering is nowhere defined.** No document numbers Kokomi's table sessions; whether the 2026-08-01/02 holdout is G5's trigger (F6) is interpretation. A one-line numbering note would make the fork's trigger falsifiable.
2. **backlog §3 numbered items 4/6/8** were ruled by R87 but the entries themselves are not struck through per the register's own retirement rule — the preamble carries the rulings, the list does not. (Same doc both sides, so no cross-doc cite.)
3. **R1–R38 are unresolvable as citations.** Early "R" numbers exist only inside prose entries and archived ruling docs (e.g., R8, R14, R24 cited as standing law); no index maps R-number → dated entry. Nothing contradicts them, but a citation audit cannot resolve them mechanically.
4. **D5 vs the 08-01/02 session:** whether any Kokomi observation from the three-seat holdout was carried into stability-band reasoning (which D5 would require labeling) is not recorded either way.
5. **R57's ref_ironclad 12× anchor swing** was "flagged for the Furina/roster workstream and NOT acted on here"; R68's Cell discipline plausibly answers it, but no doc closes the flag by name.
6. **`docs/pending/`** exists in the docs tree and is indexed nowhere in `docs/README.md`; contents not opened.

---

## 5. Coverage

**Read fully:** `tier0/DECISIONS.md` (3,371 lines, all entries 1–93 + R39–R97 + D2–D5, running index maintained); `klee-mod/DECISIONS.md` (2,396 lines, C1 through the Neap Tide addendum incl. R73–R80); `teyvat-spire-design-principles.md`; `klee-character-design.md`; `furina-kickoff-v0.1.md`; `kokomi-kickoff-v1.md`; `axis-validity-session-charter.md`; both countersign packages (`axis-validity-countersign-2026-08-04.md`, `understudy-countersign-2026-08-04.md`); `open-playtest-items.md`; `missed-requirements.md`; `red-pen-2026-07-26.md`; `backlog-2026-07-29.md`; `tech-debt-audit-2026-07-26.md`; `epoch-1-log-2026-07-26.md`; `docs/README.md`; `sprint-axis-validity-track-a-log-2026-08-04.md`; `sprint-understudy-p1-log-2026-08-04.md`.

**Opened partially, to verify citations:** `kokomi-playtest-protocol.md` (header, standing-flags, Answers, known-gaps); `playtest3-notes-2026-07-28.md` (head); `sprint-sim-hygiene-log-2026-07-29.md` (Task 1 + stamps); `silent-pilot-review-2026-07-27.md` (grep for DRAFTER stamps); `role-tempo-review.tsv` / `role-tempo-floors.yaml` (headers); `docs/furina-cards.yaml`, `docs/mondstadt-companions.yaml`, `tier0/content/characters/klee.yaml` (cited lines); `tier0/constants.py` (version stamps); `tier05/run_metrics.py` / `tier05/draft.py` (existence checks); one read-only runtime check (`score_offer("crowd_work")` = 0.0 under the live D13 tree, supporting F2).

**Did not open:** `docs/archive/` (relied on `docs/README.md`'s archive map and in-corpus citations); the remaining sprint logs (`curtain-call`, `take-a-bow`, `serenitea-sweep` I/II, `salon-ui`, `fanfare-rework`/`-compensation`, `pilot-gap`, `kokomi-instrument`, `tooling-hardening`, `bugfix`, `fontaine-rares-banner`, `silent-anchor`, `animation-sprint-2`); `understudy-phase0-report.md` and `understudy-kickoff-brief.md` (grep-verified only); the research docs; `role-tempo-baseline.md`/`-tagthrough.md`/`-debt.tsv` bodies; the C# tree beyond cited lines; `docs/pending/`. Any inconsistency living wholly inside those files is outside this audit's evidence and was not asserted.

Nothing in the repository was created, edited, or deleted; no state-changing git command was run. Every "PROPOSED" above is a map annotation for the user's pen, not an action taken.
