# Docs index

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

Reorganized 2026-07-26 (project recap). Two kinds of documents live here:

- **`docs/*.md`** — the current set: anything still governing, still open, or
  still the live reference for a system. Kept deliberately small.
- **`docs/archive/*.md`** — completed sprint plans/logs/reports and superseded
  rulings/specs. **Archived docs are records: they are kept verbatim and are
  not updated.** Where an archived doc contains a claim that is no longer
  true, the correction lives in the superseding doc named below or in
  `missed-requirements.md`.

The design-sheet YAMLs (`docs/*.yaml`) are the single source of truth for
card/relic/companion data and are read directly by the sims and codegen —
they are not documentation and are not part of this index's scope.

Chat is not a record. Rulings, worksheets, and results enter the repo or they
don't exist (house rule; see `archive/red-pen-2026-07-26.md` for what happens
otherwise).

---

## Current docs

### Registry (start here if you are looking something up)
| doc | what it is |
|---|---|
| `registry/identifiers.md` | **The resolver.** What every short code in this repo means — R/D/M/C numbers, world stamps, gates, findings, streams, exploit families, track letters — plus the collision table that assigns qualified forms (`S4-G1` vs `CC-G1` vs `SS-G1`…). Opened 2026-08-06 (housekeeping sweep, Track X). Zero design authority. |
| `registry/user-queue.md` | **The [USER] queue, single source of truth.** Every open item, what is asked, what it unblocks, and where the full text lives — the four one-word replies, the reconciled S4 gate queue, the four HELD flags, the owed sittings, the Last Call asks, the four paperwork one-liners, table time, art debt. Other documents keep their full text and point here for *status*. |
| `registry/known-identifiers.tsv` | **GENERATED — do not hand-edit.** The grandfathering snapshot `tools/lint_identifier_registry.py` diffs against. Refresh: `python tools/lint_identifier_registry.py --update-baseline`. |
| `registry/stage-clear-digest-2026-08-06.md` | REFERENCE. **The one-page digest of the R119 charter work** (Class-P purge + Clear the Stage): what landed with its revert handles, what stayed, what is asked of [USER]. Opens the Class-P §3 objection window — flagged rows revert by handle; silence ratifies. |

### State of the project (start here)
| doc | what it is |
|---|---|
| `tier0/DECISIONS.md`, `klee-mod/DECISIONS.md` | The living decision logs (sim-side and mod-side). The project's spine. Since 2026-08-06 (R-D split) the tier0 ledger's R39–R99 range lives verbatim in `tier0/DECISIONS-archive-R39-R99.md`; resolve any R-number via `registry/identifiers.md` §3, and grep the `DECISIONS*.md` globs, not one file. |
| `dockets/engineering-backlog.md` | **The engineering half of "what is open".** Work that needs no [USER] ruling to start: confirmed defects, measurement defects, unbuilt instruments, content work with nothing in front of it. Opened 2026-08-06 (Track Z). |
| `archive/red-pen-2026-07-26.md` | REFERENCE (moved to the archive 2026-08-06, Track R-B). The most recent ratification record; carries its own errata and the one still-owed Queue 5 cell (`S4-G16`). |
| `open-playtest-items.md`, `missed-requirements.md`, `backlog-2026-07-29.md`, `sitting-prep-2026-08-05.md`, `surplus-week-manifest-2026-08-05.md` | **RETIRED AS REGISTERS 2026-08-06 (Track Z / Z-3), now REFERENCE.** Each keeps its full text and its evidence, and each carries a banner saying where its open rows went — the [USER] ones to `registry/user-queue.md` §10, the engineering ones to `dockets/engineering-backlog.md`. Read them for *reasoning*, never for *status*. |

### Lifecycle statuses — what a header line means

Every `.md` and `.yaml` file under `docs/` opens with one of three lifecycle
headers, added 2026-08-06 by the docs diet (Track Z / Z-1):

- **LIVING** — expected to change; read it to work on the project. 59 files.
- **REFERENCE** — a frozen record: sprint logs, countersign packages, playtest
  records, research harvests, retired registers. Read it when something cites
  it; do not maintain it. 205 files.
- **ARCHIVED** — superseded, kept verbatim, never updated; lives in
  `docs/archive/`. 66 files.

Eighteen files (generated artifacts, TSV/JSON/TXT/PNG) cannot carry a header
and are indexed instead. The full per-status index — including the LIVING set
with a reason on every entry outside the living-doc budget — is
`registry/identifiers.md` §15.

**Where an open item may live:** `registry/user-queue.md` if it needs [USER],
`dockets/` if it is routed and not decided. Nowhere else, and a lint enforces
it on new documents (`registry/identifiers.md` §16).

### Law and charters
| doc | what it is |
|---|---|
| `teyvat-spire-design-principles.md` | The design constitution, amended through v1.11b. |
| `klee-character-design.md` | Klee's identity charter (amended in place through pass 3). |
| `furina-kickoff-v0.1.md` | Furina's governing declaration doc (amended through 2026-07-25). |
| `kokomi-kickoff-v1.md` | Kokomi's identity-law charter (Laws 1–4 are live and machine-checked; its *numeric* sections are superseded by R56+ — read numbers from the sheets). **Also superseded, and not numeric: §3's elite-axis declaration.** R51 ruled the elite pair **A2 Scaling + A6 Utility**, replacing the kickoff's "A2 + A4 Utility"; the A4 terminology clash is discharged. (Row widened 2026-08-06, R107 / S4 finding F11 — the old fence covered numeric sections only, so it missed the one identity-level supersession in the doc.) |
| `axis-validity-session-charter.md` | The Axis-Validity charter (RATIFIED 2026-08-04, AV-G2 countersigned). Grades R87(1), revises the same-y-pools diagnosis against canon, and opens Tracks A/B/C. **A-G1 was DISCHARGED 2026-08-04 (R91); B-G1 remains open** (row corrected 2026-08-06, R107 / S4 finding F7). |

### Open sprints and live queues

> **Read this table with the lifecycle headers, 2026-08-06 (Track Z / Z-4).**
> Only four documents in it are LIVING: `animation-sprint-2-plan.md`,
> `kokomi-playtest-protocol.md`, `awaiting-user-slots-2026-08-06.md` and
> `track-b-curves.md`. *(Update 2026-08-06, R-C / P-1: the slots file is now
> also REFERENCE — three of the four remain LIVING.)* Every other row is a **completed-sprint log or a landing
> record**, and those are now REFERENCE: frozen, indexed, out of the living
> set. Their *rulings* live in the two DECISIONS ledgers; the logs are the
> derivation record. A row below that says "OPEN" means the **work stream** is
> open, not that the document is maintained — the open rows themselves were
> migrated to `registry/user-queue.md` and `dockets/` by Z-3.
>
> REFERENCE documents do not move. Four `tools/` modules cite
> `track-a-kickoff-brief.md` by path in their docstrings, and 37 `docs/` paths
> are cited from `tools/` in total; `tier0/tests/test_doc_citation_targets.py`
> now fails if a paper pass moves or renames any of them.

| doc | what it is |
|---|---|
| `animation-sprint-2-plan.md` | Open sprint: gates B5/D5/E2/F2 (and the Funnel Contract §3, still binding). |
| `animation-sprint-2-log.md` | Open sprint log; doc of record for the two unfixed Playtest-2 defects. |
| `fontaine-rares-banner-sprint-log.md` | Sprint closed in code, open on four [USER] items (§"Open, and owned by [USER]"). |
| `kokomi-playtest-protocol.md` | The protocol for Kokomi's first table time ~~(never played)~~ — **the *protocol* run has not happened (its "Answers" block is blank), but Kokomi has had table time**: exploratory plays 2026-07-25/26 (`DEC-D5`-designated as contaminating-exploratory) and a seat in the three-seat co-op holdout of 2026-08-01/02. (Row corrected 2026-08-06 by the housekeeping sweep, Track X — same class as S4 finding F17, which R107 executed on `open-playtest-items.md` §2 but which was never swept through this index row.) Where it conflicts with `open-playtest-items.md` §2, the latter wins (newer). |
| `awaiting-user-slots-2026-08-06.md` | ~~Three prepared landing slots, **AWAITING [USER]**~~ — grew to seven slots, **all ANSWERED and LANDED 2026-08-06** (Track Y; R115; R118); each landed form marked in place, unselected forms struck. **FROZEN to REFERENCE 2026-08-06** (Clear the Stage R-C / P-1, excision-log E-2). Indexed 2026-08-06 (Track X). |
| `sitting-record-predraft-2026-08-06.md` | [USER]'s verdicts of 2026-08-06, transcribed **verbatim** and committed before anything was executed from them. The authority document behind R107–R112. Indexed 2026-08-06 (Track X). |
| `sitting-prep-2026-08-05.md` | The Last Call sitting's single entry point. **Still live for §8 (the four paperwork one-liners) and §10 (the batch's own asks)** — status for both is reconciled in `registry/user-queue.md` §5/§6. Indexed 2026-08-06 (Track X). |
| `surplus-week-manifest-2026-08-05.md` | INDEX for surplus week (`SW-S1…S15`), the Last Call/House Lights addendum, and the Second Wind batch's landings and replies. Indexed 2026-08-06 (Track X). |
| `pending/` | Adopted-but-retained proposal documents (`SS-G3` the CI argument, `SS-G4` the session-isolation argument), kept as the standing reasoning behind two live policies. Index: `pending/README.md`. **Indexed 2026-08-06 (Track X) — S4 §4 lead 6 recorded that this directory was indexed nowhere.** |
| `archive/run-model-rework-plan.md` | Implemented (Passes 1–4 shipped); kept current for §10.9, the living skip backlog. |
| `archive/tier05-perf-and-ironclad-act3-notes.md` | Perf pass record; kept current for §1.5.2's open items (out-of-scale boss audit lives only here). |
| `tech-debt-audit-2026-07-26.md` | The architecture audit; kept current for §9 (the big-push sequencing, with D3's pin-batch pull marked in place) and §10, the horizon list of open design sessions. |
| `epoch-1-log-2026-07-26.md` | EPOCH 1's landing record: what moved, what was archived, and the graded predictions, **plus the D10-world canonical-cell baseline — ARCHIVED by the D12 and D13 bumps** (R87(3)). Current anchors: `sprint-sim-hygiene-log-2026-07-29.md`, ratified as measurements by R107(a). (Row corrected 2026-08-06, R107 / S4 finding F16 — it previously called these numbers "the current canonical-cell baseline", two world bumps behind the stamp.) |
| `track-a-kickoff-brief.md` | Track A's execution brief (T1–T4). Executed 2026-08-04. |
| `sprint-axis-validity-track-a-log-2026-08-04.md` | **OPEN, and the doc of record for P1's binding null.** §0 holds the graded predictions; §3 diagnoses why the null fired; §4 is the stop-and-surface list; §6 is what [USER] gate A-G1 most needs to look at. |
| `handback-note-2026-08-04.md` | [USER]'s hand-back note opening the validation-soak + Track B session, verbatim. |
| `sprint-understudy-p1-log-2026-08-04.md` | The bot-playtest apparatus. **P1 VALIDATED** (clean N=3, R98); carries the eleven harness defects and the two debts still open. |
| `sprint-track-b-curves-log-2026-08-04.md` | **OPEN.** Track B's two feeds: what shipped, the live-shared-surface cross-session note, the graded pre-registrations, and the reversibility ledger (incl. the standing mod redeploy). |
| `track-b-curves.md` | **GENERATED — do not hand-edit.** B1 (demand) and B2 (output) curves, per feed. Rebuild: `python tools/track_b_curves.py --out docs/track-b-curves.md`. Empty cells are empty on purpose. |

### Dockets (routed, not decided)
| doc | what it is |
|---|---|
| `dockets/` | Holding places for items that have been **routed** and not decided. Opened 2026-08-06 by the sitting's S13 routings (R109–R111): `klee-rework.md` (X1 note + FLAG-1 held, X7 law + Track T's audit slot, X8 findings slot), `kokomi-workshop.md` (X9), `companion-pricing.md` (X10 as a CANDIDATE, explicitly not ratified), `watch-items.md` (X4/X6/X12 with their triggers), and — added 2026-08-06 by Track Z — `engineering-backlog.md` (`EB-1`…`EB-41`). Index and house rules: `dockets/README.md`. |

### Live references
| doc | what it is |
|---|---|
| `roster-codegen.md` | Codegen + build-path reference (see dated correction note in-file). |
| `upgrade-conventions.md` | Mined StS2 upgrade grammar (durable) + house rules (see dated correction note in-file). |
| `calibration-notes.md` | Battery-calibration law ("battery adapts to the roster") + the parked A3/A4 axis questions. |
| `archive/klee-real-battery-calibration.md` | The real-Ironclad baseline pipeline reference (both reproduce commands live). |
| `role-tempo-baseline.md` | The five canon pools' (solve × tempo × rarity) matrix, DLL-derived. Percentages only — no canon card text is ever committed (.gitignore:28). Also holds the wiki-vs-DLL count reconciliation. |
| `role-tempo-floors.yaml` | The machine-readable coverage floors (min-of-canon over the cells all five pools are non-zero in). Read by `tools/lint_role_tempo_coverage.py`. |
| `role-tempo-review.tsv` | **LANDED 2026-08-04 (R91)** — all 219 rows, both fields, on all three sheets; 135 divergences resolved to zero. Kept as the derivation record. (Row corrected 2026-08-06, R107 / S4 finding F7; it previously read PROVISIONAL and named A-G1 as the blocker.) |
| `role-tempo-tagthrough.md` | **PROVISIONAL.** Token → roles-cashed-into, per fight band. The artifact A-G1 reviews: a token's payoff set is a design fact. |
| `role-tempo-debt.tsv` | The 30 pinned coverage gaps the lint's `--gate` measures new findings against. ~~Delete it with P1's null.~~ **Deletion rule is R90/1a's: the debt list is deleted when the reworks address the gaps, not before** (row corrected 2026-08-06, R107 / S4 finding F7 — the "delete with P1's null" wording survived from the pre-countersign draft). Caveat that travels with the file: 30 → 19 was not eleven wins. |
| `art-sprint-spec.md` | The art pipeline regime: tiers, SOURCES.tsv/plan.tsv discipline, lint gates. |
| `art-asset-manifest.md` | The per-character asset bill ("AS SHIPPED" maintained in place). |
| `furina-art-pass-requirements.md` | Furina's art bill/spec (count delegated to `tools/art_coverage.py`). |
| `kokomi-art-pass-requirements.md` | Kokomi's art bill/spec + §6 open rulings (§1's "zero exist" predates the shell shipping — see header). |

### Research (inputs, still ground truth)
| doc | what it is |
|---|---|
| `archive/sts2-map-and-events-research.md` | Map/events wiki harvest; fidelity ruling and §5 constants stamped. |
| `archive/act2-act3-roster-research.md` | Act 2/3 enemy roster harvest the curated pools were cut from. |
| `archive/companion-value-vs-colorless-study.md` | Empirical backing for principles §4.7 and R59. |

---

## Docs diet — 2026-08-06 (Track Z, "Empty the Green Room")

Paper only. **No ruling, measured value, verdict or countersigned text was
deleted or reworded**, and nothing was moved: content that changed status
changed it in place, with a banner saying so.

**Counts, before and after.**

| | before | after |
|---|---|---|
| files under `docs/` declaring a lifecycle status | 0 | 312 in-file + 18 indexed = **330** |
| documents this index presented as current/live | 54 rows | **59 LIVING** |
| REFERENCE (frozen; read when cited) | — | **205** |
| ARCHIVED (in `docs/archive/`) | 66 | **66** — nothing new was archived |
| registers answering "what is open" | 8 | **2** — `registry/user-queue.md` and `dockets/` |

**Why the archive is unchanged.** Every file under `docs/` is cited by at
least one live artifact, test, tool or ledger; archiving any of them would
break a citation to fix a status. REFERENCE-in-place gives the same reader
benefit at zero citation cost, and
`tier0/tests/test_doc_citation_targets.py` now fails if a future pass moves a
citation target anyway.

**The acceptance test — "what do I read to get current?"** Six documents:

1. `registry/user-queue.md` — everything open, and whose it is.
2. `tier0/DECISIONS.md` — what was decided, sim side.
3. `klee-mod/DECISIONS.md` — what was decided, mod side.
4. `teyvat-spire-design-principles.md` — the law the decisions answer to.
5. `dockets/README.md` — what is routed and not decided.
6. `README.md` (this file) — which document is which.

Everything else is reached from one of those six. The five-line "how to find
anything" note is `registry/identifiers.md`, above §1.

## Archive review — 2026-08-06 (housekeeping sweep, Track X)

A conservative archive pass ran over the current set. **Nothing was moved.**
The rule applied was the sweep's own: *when in doubt it stays live and gets a
status header instead.* Recorded so the pass is not re-run blind:

| Candidate | Why it looked archivable | Why it stayed live |
|---|---|---|
| `track-a-kickoff-brief.md` | Track A executed 2026-08-04; the track log is the doc of record | Four `tools/` modules cite it by path in their module docstrings (`canon_role_tempo.py`, `suggest_role_tempo_tags.py`, `lint_role_tempo_coverage.py`, `role_tempo.py`). Moving it makes four live citations stale to fix one index row. **Status header added in-file instead.** |
| `understudy-kickoff-brief.md`, `understudy-phase0-report.md`, `archive/understudy-p0-findings.md` | Phase 0 closed; rulings landed as R93–R97 | The Understudy sprint is open (`UND-P1.5` is next, R104), and `understudy/README.md`, `understudy/soak.py`, `vendor/README.md`, `vendor/STS2_MCP/PROVENANCE.md` and `docs/atlas/vendor-sts2-mcp.md` all cite them as live provenance |
| `sitting-record-predraft-2026-08-06.md` | Its content landed as R107–R112 | It is the **verbatim** [USER] authority document those six rulings are drawn from; the rulings cite it |
| `handback-note-2026-08-04.md` | The session it opened has closed | Verbatim [USER] text, cited by R97; verbatim records are not edited or relocated by a paper sweep |
| `pending/serenitea-g3-ci-proposal.md`, `pending/serenitea-g4-session-isolation.md` | Both ADOPTED | `pending/README.md` explicitly retains them as the standing argument — *"read it before adding a job"* |
| `brief-*.md` (three) | Briefs, not sprints | All three are cited as the live filing target by R87, R92/3c and the backlog |

## Archive map

Grouped by thread; each line says why the doc is closed and where its live
successor is. "→" = superseded by / continued in.

### Clear the Stage, Track R-B — 2026-08-06 (43 REFERENCE records)

The R-B demotion (charter R119, rail 1) moved **43 REFERENCE files verbatim**
from the docs root into `docs/archive/`. Each carries a dated move banner
naming its old and new path; the per-file map — old path, new path, which
citers were repointed, which frozen citers were knowingly left stale (M2) —
is `review/stage-clear/rb-move-manifest.tsv`. Their lifecycle status is
unchanged (REFERENCE, relocated); nothing below a move banner was edited.
Ledger-cited REFERENCE files did **not** move (rail 1: the append-only
DECISIONS ledgers cannot be repointed) — that policy question is queue row
**Q20**.

### Tier 0 / Tier 0.5 simulator thread
- `tier0-simulator-spec.md` — origin charter (M1–M4). The world outgrew it on
  purpose: cards live in `docs/*.yaml` not `content/cards/`, Frozen is v2,
  the non-goals (relics/potions/upgrades/maps) all shipped sanctioned, OPS is
  46 not 14. Axis definitions (§6) remain the historical source of the
  scorecard; the living law is `tier0/harness/axes.py` + DECISIONS.
- `tier05-draft-sim-spec.md` — → `run-model-rework-plan.md` (template v1 is
  DEAD as of RUNTEMPLATE v6; real maps/acts/events shipped).
- `tier05-m5-report.md` … `tier05-m8-report.md` — milestone reports, all
  worlds long superseded (M6/M7 carry their own ARCHIVED banners).
- `m7-rulings.md`, `m8-rulings.md` — executed ruling records. Durable laws
  they created (conjunctive healing law; dose-cells-are-diagnostics) live in
  the principles doc and DECISIONS.
- `errata-m5-triage.md` — both items landed. Its finding 2 (catalysts
  structurally suppress Frozen) is preserved in DECISIONS.
- `csharp-build-spec.md` — C1–C3 delivered (three characters, not one);
  localization shipped inline rather than as JSON. The never-built C2
  per-fight telemetry is logged in `missed-requirements.md` §2.3.
- `c3-codegen-gap-list.md` — every gap closed (68 generated + 8 hand-written,
  zero system-blocked).
- `relic-potion-layer-plan.md` — W1/W2/W3 fully implemented
  (`tier05/relics.py`, `potions.py`, content YAMLs); header's DRAFT status is
  historical.

### Cross-roster passes and triage
- `pass1-rulings-round2.md` → `pass2-rulings-round3.md` → `pass3-ratification.md`
  — each superseded the last; pass-3's frozen-scorecard closeout was itself
  superseded by `run-model-rework-plan.md` §0 ("the battery itself is broken").
- `morning-triage-rulings.md`, `triage-execution-report.md` — executed in full.

### Klee thread
- `klee-pass-1-report.md`, `klee-pass-2-report.md`, `klee-pass-3-report.md` —
  pass reports; v0.1 baseline replaced by `V02_MEDIAN`.
- `klee-pass-4-plan.md` — its headline numbers are all false now (the survival
  sprint fixed A6 via its own option (c)); asks A3/A5 were never ruled — logged
  in `missed-requirements.md` §2.5, Tier 5.
- `klee-r23-r25-rulings.md`, `klee-session-worknote.md`, `klee-errata-report.md`
  — executed ruling/worknote records.
- `klee-design-review.md` — framing (40% Ironclad target) invalidated by
  `klee-real-battery-calibration.md`; two of its four dead-card reworks never
  landed — logged in `missed-requirements.md` §3.4.
- `klee-survival-sprint-plan.md` → `klee-survival-sprint-report.md` — shipped;
  bands went floor-only per its recommendation. The telemetry gate it imposed
  is logged in `missed-requirements.md` §2.2.
- `klee-art-redpen-round2.md` → `klee-art-redpen-round3.md` — art verdicts
  re-litigated at true card size, then ruled 2026-07-21 (record in
  `art/plan.tsv` DECLINE rows).

### Furina thread
- `furina-predesign-notes.md` — Part 2 → `furina-kickoff-v0.1.md`; Part 1
  (Frozen v2 errata) is settled principles v1.5.
- `furina-sprint-1-plan.md` / `-redpen.md` / `-report.md` — sprint 1 delivered
  and resolved.
- `furina-pass1-rulings.md`, `furina-pass3-rulings.md` — R16/R17 architecture
  retired by R40–R43. R29d's owed naming/lore pass is logged in
  `missed-requirements.md` Tier 5.
- `furina-sheet-pass-{1,2,3}-plan/-report.md` — sheet passes; every measured
  world (CONSTANTS/DRAFTER/RUNTEMPLATE) since replaced. Pass-3's unruled asks
  are logged in `missed-requirements.md` §3.6/§3.7.
- `furina-sheet-pass-4-plan.md` — Q1 re-ruled, Q2 dissolved by the fanfare
  sprint; the orphaned Q3 directive is logged in `missed-requirements.md` §1.5.
- `furina-sheet-redpen.md` — flags executed or ruled; flag 8's convergence
  cell is the one still owed, tracked in `red-pen-2026-07-26.md`.
- `furina-principles-amendment-batch.md` — ratified as principles v1.10.
- `furina-salon-rework-plan.md` — Salon v2 shipped (R40); its §6(c)/(d)
  residue is logged in `missed-requirements.md` §3.6.
- `furina-tier05-baseline.md` — diagnostic; superseded by R40–R43; Spotlight
  redesign inheritance tracked in the pool-sweep backlog.
- `furina-legibility-sprint-log.md`, `furina-fanfare-sprint-log.md` — closed
  sprints (fanfare CLOSED by ruling, null confirmed twice).

### Kokomi thread
- `kokomi-session-worknote.md` — all 18 items landed ("no mod presence" line
  is historical; she has a full C# tree now).
- `kokomi-roster-v0.1-report.md` → `kokomi-sheetpass-v0.2-report.md` →
  `kokomi-v0.4-plan.md` → `kokomi-v0.4-report.md` — the v0.1/meter-50 →
  v0.4b/R56 arc; each superseded by the next, final numbers by R57/R58.
  Unbuilt asks (stability band, multiplicative cell, P3/P4) are logged in
  `missed-requirements.md` §§1.3, 1.4, 3.2.

### Art / animation thread
- `art-taste-pass.md` — → `klee-art-redpen-round2/3.md`; its four process
  directives all live in `tools/art_lint.py` + `art/plan.tsv`.
- `companion-art-plan-addendum.md`, `companion-lore-errata.md`,
  `sprint-addendum-art.md` — executed in full (cover_autocrop, sibling
  carve-out, Dahlia renames, dedupe lint).
- `animation-sprint-1-plan.md` / `-log.md` — sprint 1 CLOSED 2026-07-24; its
  deferred "polish sprint" scenes are logged in `missed-requirements.md` §4.5.
- `icon-gap-2026-07-24.md` — sweep landed; **caution:** its "all 78 Furina
  card portraits resolve" claim checked path resolution, not files — see
  `missed-requirements.md` §4.1.

### Shop / ship-what-we-know / playtests
- `shop-companion-channel-plan.md` → `shop-companion-channel-sprint.md`
  (pre-registration, kept verbatim) → `shop-companion-channel-sprint-log.md`
  — built and measured; §7 close-out items tracked in
  `open-playtest-items.md` §6.2 except §7.6/§7.7 (logged in
  `missed-requirements.md` Tier 5). Its "Fontaine has zero Rares" note is
  stale since `15fc78f`.
- `ship-what-we-know-sprint-plan.md` / `-log.md` — sprint CLOSED at the
  red-pen; the log's "What is NOT done" list is mostly overtaken by
  `red-pen-2026-07-26.md` (which is the authoritative close-out).
- `playtest-2026-07-25-coop-a0.md` — playtest record; carries the co-op scope
  rulings R1's sealing comment points at. Its "Furina still does not
  [register an upgraded form]" line closed the next day (R2, queue 3).
