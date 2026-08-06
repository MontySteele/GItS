# Identifier registry — what every short code in this repo means

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status: RESOLVER.** Opened 2026-08-06 by the housekeeping sweep (Track X) of
the "Strike the Set" batch. This file carries **zero design authority**. It
decides nothing, grades nothing, and rewrites nothing: every meaning below is
copied from the document that minted it, and where a status is recorded it is
the status that document (or a later ruling) already states.

**What it is for.** The repo mints short codes freely — gates, findings,
streams, tracks, world stamps — and several of them collide. This file answers
two questions and only two:

1. *What does this identifier mean?* → the tables below.
2. *Which of the several things called `G1` is meant here?* → §2, the collision
   table, which assigns a **qualified canonical form** to each mint.

**The resolution rule, stated once.** Collisions are resolved by
**qualification, not renumbering**. No identifier anywhere in this repo is
renumbered by this sweep. Existing prose keeps its bare tokens; this registry
is the resolver a reader consults. Only references that a reader genuinely
cannot disambiguate were repaired inline, and each such repair is listed in the
sweep report. New documents should use the qualified form for any token in §2.

**Companion file:** `docs/registry/user-queue.md` — the single source of truth
for what is open and for whom.

---

## How to find anything now — five lines

1. **"Is this still open, and whose is it?"** → `docs/registry/user-queue.md` if it needs [USER]; `docs/dockets/` if it is routed and not decided. Those two are the **only** homes an open item has (§16), and a lint keeps it that way.
2. **"What did we actually decide?"** → `tier0/DECISIONS.md` (R39–R120, `DEC-D2`–`DEC-D5`) and `klee-mod/DECISIONS.md` (R73–R80); one shared R-sequence, CI-checked for duplicates. R1–R38 are not mechanically resolvable — see §3.
3. **"Do I have to read this document?"** → its **lifecycle header**, the line under the title: LIVING = yes, keep it true; REFERENCE = only when something cites it; ARCHIVED = history only. The full per-status index is §15; the 59 LIVING files are listed there.
4. **A short code you don't recognise** (`G6`, `D5`, `C1`, `P1.5`, `X5`, `NC-1`, `S-2`) → §1 for the namespace, §2 for the collision table, which names the qualified form and the document that minted it.
5. **"Can I quote this number?"** → check its world stamp against §4 (`RT7 / D14 / P3 / C5` today). A bump archives the numbers below it; archived numbers are bannered where they are published, never rewritten (R101b).

**"What do I read to get current?"** — six documents, in this order:
`docs/registry/user-queue.md` → `tier0/DECISIONS.md` → `klee-mod/DECISIONS.md`
→ `docs/teyvat-spire-design-principles.md` → `docs/dockets/README.md` →
`docs/README.md`. Everything else is reached from one of those six.

---

## 1. Namespace summary

| Namespace | Shape | Population | Minting authority | Collides? |
|---|---|---|---|---|
| Rulings | `R<n>` | R1–R120 | `tier0/DECISIONS.md` + `klee-mod/DECISIONS.md` (one shared sequence) | R1–R38 unresolvable as citations — see §3 |
| D-series rulings | `D<n>` | D2–D5 | `tier0/DECISIONS.md` | **yes** — with DRAFTER stamps and with sprint task-ids |
| Milestones | `M<n>` | M1–M8 | `tier0/DECISIONS.md`, `klee-mod/DECISIONS.md` | no |
| C# milestones | `C<n>` | C1–C3 | `klee-mod/DECISIONS.md` | **yes** — with world stamps and S7 candidates |
| World stamps | `RT<n>` / `D<n>` / `P<n>` / `C<n>` | RT7 / D14 / P3 / C5 | `tier0/constants.py`, `tier05/draft.py` | **yes** |
| Gates & sprint task-ids | `<Letter><n>` | very large | every sprint plan/log | **yes, heavily** — see §2 |
| S4 hygiene findings | `F<n>` | F1–F17 | `review/ledger-audit/hygiene-report.md` | **yes** — with sprint task-ids `F1`/`F2` |
| Held flags | `FLAG-<n>` | FLAG-1…FLAG-4 | `docs/sitting-record-predraft-2026-08-06.md`, R110/R111 | no |
| Exploit families | `X<n>` | X1–X14 | `review/redteam/exploit-ledger.md` | **yes** — with batch track letter X |
| Surplus streams | `S<n>` | S1–S15 | `docs/surplus-week-manifest-2026-08-05.md` | **yes** — with Track S errata `S-1…S-3` |
| Second Wind Track S errata | `S-<n>` | S-1, S-2, S-3 | `docs/surplus-week-manifest-2026-08-05.md` §"Track S" | **yes** — with surplus streams |
| Non-card parity findings | `NC-<n>` | NC-1…NC-20 | `review/parity-sweep/noncard-triage-memo.md` | no |
| Card parity families | `SYS-<n>` | SYS-1…SYS-14 | `review/parity-sweep/triage-memo.md` | no |
| Lint candidates | `L<n>` | L1–L8 (S1 memo); L1–L12 (art_lint) | `review/parity-sweep/triage-memo.md`; `tools/art_lint.py` | **yes** |
| House Lights findings | `N-<n>`, `O-<n>`, `O<slice>-<n>` | N-1; O-1; O1-1…O12-n | `docs/lore-fidelity-audit-2026-08-05.md`, `docs/instrument-redteam-2026-08-05.md` | no |
| Track T audits | `T-<n>` | T-1, T-2, T-3 | `docs/track-t-audits-2026-08-06.md` | **yes** — with Track A's task-ids T1–T4 |
| Understudy phases | `P<n>` | P0, P1, P1.5, P2 | `docs/understudy-kickoff-brief.md` + R93–R104 | **yes** — with POLICY stamp and predictions |
| Scorecard axes | `A<n>` | A1–A7 | `tier0/harness/axes.py` (law), `docs/archive/tier0-simulator-spec.md` §6 (historical) | **yes** — with Klee pass asks A3/A5 and sprint task-ids |
| Track letters | `Track <A–X>` | reused every batch | each batch's kickoff | **yes, by design** — always qualified by batch |
| Batch/sprint code-names | prose | see §12 | — | no |

---

## 2. The collision table — qualified canonical forms

This is the section the rest of the registry exists for. **A token in the left
column means several different things.** Use the qualified form when writing
new prose; use this table to resolve old prose.

### 2.1 `G<n>` — the worst collision in the repo

Seven independent mints use bare `G` numbers. Prefixes are assigned here and
are **new writing conventions, not renames**: no minting document's own numbering
changed.

| Qualified form | Bare form as written | Meaning | Minting document | Status |
|---|---|---|---|---|
| `S4-G1` … `S4-G20` | `G1`…`G20` | The 20-row undischarged **[USER] gate queue** of the S4 ledger audit | `review/ledger-audit/hygiene-report.md` §3 | see `docs/registry/user-queue.md` §2 |
| `CC-G1`, `CC-G2` | `G1`, `G2` | R86 / "Take a Bow" **Curtain Call art gates**: contact-sheet eyes-on; in-game screenshot review of the twelve cards + A0 smoke run | `tier0/DECISIONS.md` R86; `docs/take-a-bow-sprint-log-2026-07-27.md` §3 | OPEN — materials ready at `docs/g12-review-2026-08-05.md`. Tracked as `S4-G12`. |
| `SS-G1` … `SS-G4` | `G1`…`G4` | **Serenitea Sweep I** track-G items: sheet-comment lint; the `mondstadt-companions.yaml` correction; the CI proposal; the session-isolation (worktree-per-session) policy | `docs/serenitea-sweep-log-2026-07-26.md` §§G1–G4 | all ADOPTED. `SS-G3` → `.github/workflows/repo.yml`; `SS-G4` → `docs/worktree-workflow.md` |
| `NT-G2`, `NT-G3`, `NT-G5`, `NT-G6`, `NT-G7`, `NT-G8` | `G2`, `G3`, `G5`, `G6`, `G7`, `G8` | **Neap Tide v2.1** batch item labels (Kokomi pass): G2 = `before_sun_and_moon` stacking ratified over a ban; G3 = flavor-text segregation convention; G5 = the pre-registered playtest-three fork; G6 = `tactical_retreat` starter migration; G7 = the R79 verb-partition law; G8 = `swift_currents` merged into `moonlit_offering` | `klee-mod/DECISIONS.md`, "Neap Tide v2.1" + addendum | landed, except `NT-G5` (fork unfired/unevaluated — see queue) |
| `AS2-G1`, `AS2-G2` | `G1`, `G2` | **Animation sprint 2** track-G tasks: extract the common bridge base; rename `KleeAnimationRouter` → `CreatureAnimationRouter` | `docs/animation-sprint-2-plan.md` §G | both ✅ done (`docs/animation-sprint-2-log.md`) |
| `LF-G1` … `LF-G5` | `G1`…`G5` | **Track N lore-fidelity audit** coverage gaps in `lint_furina_registers.py` | `docs/lore-fidelity-audit-2026-08-05.md` §"Coverage gaps" | findings only; part of the N TOP-5 review |
| `RA-G1`, `RA-G2` | `G1`, `G2` | **Track G roster-anchor v14** document sections: the v14 anchor table; the paired D13→D14 diff | `docs/roster-anchor-v14-2026-08-05.md` §§2–3 | PROPOSED — designate-or-hold ask, sitting-prep §10.2 |
| `A-G1` | *(already qualified)* | Axis-Validity **Track A gate** — tag review | `docs/axis-validity-session-charter.md` §7 | **DISCHARGED 2026-08-04 (R91)** |
| `B-G1` | *(already qualified)* | Axis-Validity **Track B gate** — per-axis disposition of the seven-axis scorecard; carries the re-registered Fanfare P1 | `docs/axis-validity-session-charter.md` §4/§7; R90/1b | OPEN. Tracked as `S4-G5`. Now the governing condition on backlog items 1–3 and the fanfare STOP (R107/F1). |
| `AV-G2` | *(already qualified)* | Axis-Validity **charter gate** — countersign the §6.1 ratification bundle | `docs/axis-validity-session-charter.md` §7 | COUNTERSIGNED 2026-08-04 |
| `G-A5`, `G-A5(b)`, `G-F1`, `G-F2`, `G-C2`, `G-C3`, `G-D4` | *(already qualified)* | **"Ship What We Know" sprint gates**, prefix-shaped `G-<track><n>` | `docs/archive/ship-what-we-know-sprint-plan.md` | `G-A5(b)` OPEN (one capture); `G-F1`/`G-F2` landed as annotations |

**The `S4-G<n>` range, written out (added 2026-08-06, Track Y).** The row above
uses an ellipsis, which a human reads and a resolver does not. All twenty are
therefore named literally once, here, so that any document may cite any of them
without the registry lint reporting an unregistered token: `S4-G1`, `S4-G2`,
`S4-G3`, `S4-G4`, `S4-G5`, `S4-G6`, `S4-G7`, `S4-G8`, `S4-G9`, `S4-G10`,
`S4-G11`, `S4-G12`, `S4-G13`, `S4-G14`, `S4-G15`, `S4-G16`, `S4-G17`, `S4-G18`,
`S4-G19`, `S4-G20`. Their per-gate meanings and statuses live in
`docs/registry/user-queue.md` §2; this list is a resolver, not a second index.

**Pre-existing resolvers this table does not disturb.** `docs/g12-review-2026-08-05.md`
already states in its own header that *"G12 (hygiene-report row G12) = R86's G1
and G2"* — i.e. `S4-G12` = {`CC-G1`, `CC-G2`}. That statement is correct and
stands; this table simply makes it findable without opening the file.

### 2.2 `D<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `DEC-D2` … `DEC-D5` | The **D-series of `tier0/DECISIONS.md`** — D2 Neuvillette dual identity; D3 pass-4 ask A5 deferred to the axis-validity session; D4 instrument-visibility law for predictions; D5 Kokomi stability-band provenance and schedule. (`D1` was never minted.) | `tier0/DECISIONS.md` |
| `DRAFTER-D10` … `DRAFTER-D14` | **DRAFTER world stamps** — `DRAFTER_VERSION` in `tier05/draft.py`/`tier0/constants.py`. Current: **14**. A bump archives every drafter-layer number taken under the previous stamp (R87(3)). | `tier0/constants.py:951` |
| `AS2-D1` … `AS2-D5` | **Animation sprint 2** track-D tasks (the Salon stage rework). `AS2-D4` = bridge update; `AS2-D5` = the [USER] layout/composition pass, capture required. | `docs/animation-sprint-2-plan.md` §D |
| `SS-D1` … `SS-D3`, `SSII-D1`, `SSII-D4`, `SSII-D5` | Serenitea Sweep I/II track-D items | `docs/serenitea-sweep-log-2026-07-26.md`, `docs/serenitea-sweep-ii-log-2026-07-27.md` |

> **R107(a) already ruled on this collision** and its reasoning is the precedent
> this registry follows: *"the D-series in this file is the difficulty series
> (D2-D5) and 'D13' in the sim-hygiene log is a DRAFTER world stamp; two
> numbering systems sharing a token is exactly the hygiene F2 exists to stop."*

### 2.3 `C<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `MOD-C1` … `MOD-C3` | **C# build milestones** (three characters shipped, codegen, localization) | `klee-mod/DECISIONS.md`; `docs/archive/csharp-build-spec.md` |
| `S7-C1`, `S7-C2` | **S7 family-C candidate infidelities** — C1 the +2 block offset; C2 the Fanfare accounting residual. Both probed (`docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`) | `docs/s7-classification.md` |
| `CONSTANTS-C3` … `CONSTANTS-C5` | **CONSTANTS world stamps** — `CONSTANTS_VERSION`. Current: **5** (bumped by Track W for S-1's Furina cost change). | `tier0/constants.py:837` |
| `SS-C1` … `SS-C6`, `SSII-C4`, `SSII-C6` | Serenitea Sweep I/II track-C items | the two sweep logs |
| `AS2-C1` … `AS2-C4` | Animation sprint 2 track-C tasks | `docs/animation-sprint-2-plan.md` §C |

### 2.4 `P<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `UND-P0`, `UND-P1`, `UND-P1.5`, `UND-P2` | **Understudy phases** — P0 measurement; P1 the bot-playtest apparatus (VALIDATED, R98); P1.5 the bridge fork (BUILT 2026-08-05, promoted NEXT by R104); P2 hard-state turn sampling (amended default, R94) | `docs/understudy-kickoff-brief.md`; R93–R104 |
| `POLICY-P3` | **POLICY world stamp** — `POLICY_VERSION` in `tier05/draft.py`. Current: **3**. The `P3` of the `RT7 / D14 / P3 / C5` world string. | `tier05/draft.py:1329` |
| `NT-P1` … `NT-P9` | **Neap Tide predictions** P1–P9, graded in place | `klee-mod/DECISIONS.md`, "Predictions" |
| `SHOP-P1` … `SHOP-P3` | Shop-companion-channel phases, graded at §7 close-out | `docs/archive/shop-companion-channel-sprint-log.md`; R63 |
| `BUG-P1`, `BUG-P2` | Backlog §1 bug priority bands (C# P1 / C# P2) | `docs/backlog-2026-07-29.md` §1 |

### 2.5 `T<n>` / `T-<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `TA-T1` … `TA-T4` | **Track A execution brief tasks** (role/tempo tooling) | `docs/track-a-kickoff-brief.md` |
| `TT-T1`, `TT-T2`, `TT-T3` | **Track T audit sweeps** of the Second Wind batch — T-1 = family X2, T-2 = family X7, T-3 = family X8 | `docs/track-t-audits-2026-08-06.md` |

### 2.6 `S<n>` / `S-<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `SW-S1` … `SW-S15` | **Surplus-week streams** (see §7) | `docs/surplus-week-manifest-2026-08-05.md` §1 |
| `SW2-S-1`, `SW2-S-2`, `SW2-S-3` | **Second Wind Track S errata** — the batch's only behaviour changes (X3 Encore Performance; X11 `replay_next_companion`; X14b ethereal-spotlight fallback) | `docs/surplus-week-manifest-2026-08-05.md` §"Track S" |
| `VAL-S7` | A step id in `klee-mod/build/validate.ps1` (the auto-mode suite step), cited in `.github/workflows/repo.yml` | `.github/workflows/repo.yml` |

### 2.7 `X<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `S13-X1` … `S13-X14` | **Exploit mechanism families** (see §8) | `review/redteam/exploit-ledger.md` |
| `Track X` (Strike the Set) | This batch's housekeeping track — a *track letter*, not an exploit family | this sweep |

### 2.8 `L<n>`

| Qualified form | Meaning | Minting document |
|---|---|---|
| `ART-L1` … `ART-L12` | **`tools/art_lint.py` rule numbers** (L1 one-producer-per-out-path, L7, L9 family ban, L12 duplicate crops…) | `tools/art_lint.py`; `docs/art-sprint-spec.md` |
| `S1-L1` … `S1-L8` | **S1 triage lint candidates** — proposed checks, not implemented rules | `review/parity-sweep/triage-memo.md` §"lint candidates" |
| `UPG-L1` | `tools/lint_upgrade_coverage.py` rule L1 (an upgrade entry may not be empty) | `tools/lint_upgrade_coverage.py` |

### 2.9 `A<n>`, `F<n>`, `B<n>`, `E<n>` and the general rule

Almost every sprint plan in this repo numbers its own tasks `<TrackLetter><n>`.
That is a **document-scoped** namespace and the registry does not enumerate it
exhaustively — doing so would be a list of several hundred rows that nobody
reads. The rule instead:

> **A `<Letter><n>` token means whatever the document you are reading minted it
> as. If you are citing one *outside* its minting document, qualify it.**

The registry enumerates only the tokens that have **escaped** their minting
document — i.e. that are cited elsewhere in the repo without their document —
because those are the ones a reader cannot resolve. Escapees found by this
sweep are all in §2.1–§2.8, plus:

| Token | Escaped meaning | Minting document |
|---|---|---|
| `A1`…`A7` | The **seven scorecard axes** (A2 Scaling, A6 Utility, …). Cited constantly outside any sprint. | `tier0/harness/axes.py`; historical definitions in `docs/archive/tier0-simulator-spec.md` §6 |
| `A3`, `A5` (Klee) | **Klee pass-4 asks** A3 (archetype-band deviation) and A5 (scorecard invariants) — *not* axes A3/A5 | `docs/archive/klee-pass-4-plan.md`; `docs/missed-requirements.md` §2.5, Tier 5 |
| `A0` | The **A0 smoke run** — a co-op boot check, not an axis | `docs/archive/playtest-2026-07-25-coop-a0.md`; R86 |
| `F1`, `F2` (Serenitea Sweep II) | Track-F items: `F1` the roster registry + gate; `F2` the bootstrap headline | `docs/serenitea-sweep-ii-log-2026-07-27.md` |
| `E1`, `E2`, `E2b` (Neap Tide) | Kokomi measurement cells; `E2b` is the accrual-arm decomposition | `klee-mod/DECISIONS.md` |
| `B2`, `B3` (Last Call) | The two probes in flight at the Last Call batch tip | `docs/surplus-week-manifest-2026-08-05.md` addendum |

---

## 3. `R<n>` — rulings

**One shared sequence across two ledgers.** `tier0/DECISIONS.md` and
`klee-mod/DECISIONS.md` draw from the *same* R-number space — R73–R80 are
minted in `klee-mod/DECISIONS.md` (Neap Tide), R39–R116 in
`tier0/DECISIONS.md`. CI enforces no duplicates across both files
(`.github/workflows/repo.yml`, job `ledger`).

| Range | Where | Note |
|---|---|---|
| R1–R38 | prose entries and archived ruling docs | **Not mechanically resolvable.** S4 §4 lead 3: *"no index maps R-number → dated entry."* Several (R8, R13, R14, R24, R25, R29d, R34–R38) are cited as standing law. Resolving them is an open paper item — see `docs/registry/user-queue.md` §4. |
| R39–R72 | `tier0/DECISIONS.md`, `## R<n>` headings | dated, resolvable |
| R73–R80 | `klee-mod/DECISIONS.md`, Neap Tide v2.1 | dated, resolvable |
| R81–R120 | `tier0/DECISIONS.md` | dated, resolvable. **Current maximum: R120** (2026-08-06). |

**The Cold Reading batch (2026-08-06) minted four**, listed so they resolve
without opening the ledger: **`R113`** the C2 escrow released and its four
fanfare marks struck; **`R114`** the four held flags ruled; **`R115`** the
`NT-G5` fork's non-observation record, the Kokomi gate re-anchor, and the
corpse-detonation probe staged; **`R116`** five S14 canonicity questions ruled
and Errata Batch 2 constituted.

**The wave-8 ratified-execution batch (2026-08-06) minted three**: **`R117`**
Q13/Q14/Q15 ruled (*"14) Yes · 13) I'd say A · 15) Widen"* — v6 stamp, α
boss-room scope, citation-lint widening) and the `Q16` rider minted;
**`R118`** the eleven-reply sitting batch (Q5/Q6/Q7/Q9/Q10/Q11/Q16/animation
FREE-SPIKE; 10.2/10.7/10.8 incl. the R88 amendment; the §3 paperwork trio);
**`R119`** the Class-P charter signed (*"Oops - yes, charter is AUTHORIZEd"*)
and the "Clear the Stage" refactor charter authorized in full; **`R120`**
dispatch (d)'s four replies (the Klee "Catalytic Converter" rename, 10.1's
`grand_gala` art release, 10.3 staged as D15 pending 10.7, probe (d)
countersigned).

Sub-clause citation shape is `R<n>/<clause>` (e.g. `R90/1c`, `R91/2b`) or
`R<n>(<letter>)` (e.g. `R107(a)`). Clause letters belong to their own ruling:
`R90` carries 1a/1b/1c, `R91` carries 2a–2d. A lint for exactly this class of
misattribution is **staged, not merged**, on `staged/f14-siblings`.

---

## 4. World stamps

Four independent version stamps, quoted together as a world string
(`RT7 / D14 / P3 / C5`). A bump archives numbers measured under the prior stamp;
archived numbers are **bannered where published, never rewritten** (R101b).

| Stamp | Constant | File | Current |
|---|---|---|---|
| `RT<n>` | `RUNTEMPLATE_VERSION` | `tier0/constants.py:628` | **7** |
| `D<n>` | `DRAFTER_VERSION` | `tier0/constants.py:951` | **14** |
| `P<n>` | `POLICY_VERSION` | `tier05/draft.py:1329` | **3** |
| `C<n>` | `CONSTANTS_VERSION` | `tier0/constants.py:837` | **5** |

---

## 5. `F<n>` — S4 hygiene findings

Seventeen findings, `review/ledger-audit/hygiene-report.md` §2.
**All seventeen APPROVED AS PROPOSED by R107**; sixteen executed by the Second
Wind batch (Track R), **F6 blocked** on a fact nobody supplied.

| # | One-line | Status |
|---|---|---|
| F1 | Furina deferral chain fired; replacement condition dissolved | EXECUTED — re-pointed to Track B / `B-G1` (R107) |
| F2 | DRAFTER 13 both "landed" and "not done"; fixture mis-assigned | EXECUTED — fixture re-homed, `S4-G8` discharged (R107(a)) |
| F3 | Spotlight law text in both law docs describes the retired design | EXECUTED |
| F4 | R84's "only quotable roster table" archived, unamended | EXECUTED |
| F5 | Backlog orders an instrument the ledger records as built | EXECUTED |
| F6 | `NT-G5` fork's trigger plausibly fired, unevaluated | **BLOCKED — awaiting [USER]**, drafts parked at `docs/awaiting-user-slots-2026-08-06.md` slot 1 |
| F7 | Three `docs/README.md` index rows contradict the R92-era discharge | EXECUTED |
| F8 | Principles §4.7 asserts a roster fact R64 falsified | EXECUTED |
| F9 | `kurages_oath` "too strong" flag never reached the protocol | EXECUTED |
| F10 | Klee charter cites a retired two-sided band | EXECUTED |
| F11 | Kokomi kickoff elite-axis declaration superseded by R51 | EXECUTED |
| F12 | Furina kickoff §4 still lists the dead "Encore gained" leg | EXECUTED |
| F13 | Charter footer kept the corrected 402-card figure | EXECUTED |
| F14 | `role-tempo-floors.yaml` cites R91/1c for an R90/1c rule | EXECUTED — **four siblings STAGED, unmerged**, on `staged/f14-siblings` |
| F15 | missed-requirements lists two fixed sheet comments as open | EXECUTED |
| F16 | README calls an archived baseline "current" | EXECUTED |
| F17 | open-playtest-items says Kokomi has never been played | EXECUTED |

---

## 6. `FLAG-<n>` — held flags

Four clarifications carried out of the sitting of 2026-08-06 unresolved.
**Nothing may be built against a held flag** — not a probe, not a pre-draft,
not a "while we're in there" (`docs/dockets/README.md` house rule 3).

| Flag | Family | Question | Recorded at |
|---|---|---|---|
| ~~FLAG-1~~ | `S13-X1` | ~~Does the accumulator note also ride the Kokomi pool-rework docket, and does the shared uncapped state take a structural disposition?~~ | **RULED 2026-08-06 by R114** — ratified change, accumulator scopes to the writing turn in both engines |
| ~~FLAG-2~~ | `S13-X3` | ~~Two adjacent closures undisposed: copied `sucrose_catalyst_conversion` outrunning its Exhaust bound; unscoped `cost_override`~~ | **RULED 2026-08-06 by R114** — both fixes ratified; residue staged as `AB-s1` |
| ~~FLAG-3~~ | `S13-X5` | ~~Does "seems fine" cover decay-proof fanfare-floor stacking, or only the cantrip leg?~~ | **RULED 2026-08-06 by R114** — INTENDED, both legs; re-registered as watch item `W4` |
| ~~FLAG-4~~ | `S13-X14` | ~~Legs (a) `curse_poor_sleep` retain-jam and (c) Powers → `result_pile: none` remain undisposed~~ | **RULED 2026-08-06 by R114** — leg (c) intended, no guard; leg (a)'s root staged as `AB-s2` |

> **ALL FOUR FLAGS DISCHARGED 2026-08-06 (R114).** The `FLAG-<n>` namespace is
> closed unless a future sitting mints new ones. Struck rather than deleted:
> the flags are part of how these four families were decided.

---

## 7. `S<n>` — surplus-week streams

`docs/surplus-week-manifest-2026-08-05.md` §1 is the authoritative table
(tip commits and artifacts). Summary only, here:

| Stream | What | Sitting status |
|---|---|---|
| S1 | Card parity sweep, 219 cards → SYS-1…SYS-14 | open |
| S2 | Event conversion gallery, 47 events | **open — [USER] checkboxes** |
| S3 | Enemy bestiary, 111 dossiers → 5 fight classes | landed, no verdicts requested |
| S4 | Ledger consistency audit → F1–F17 + the 20-gate queue | **SAT 2026-08-06** (R107) |
| S5 | Animation-tech peek: the answer is Spine | landed |
| S6 | Mutation audit, 114 mutants / 46 survived | pinned by S15 |
| S7 | Understudy fidelity audit → families A–D, candidates `S7-C1`/`S7-C2` | **CLOSED for both candidates 2026-08-06 (R113):** `S7-C1` reclassified to family B (Frail, a reconstruction gap); `S7-C2` written off, escrow released, four marks struck. One bounded term survives and is queued (term 3, +2 Fanfare/combat, tier0-optimistic). |
| S8 | Potion + relic gallery, 51 items | 8 flagged items open |
| S9 | Weekly-boss dossiers, 11 bosses | landed |
| S10 | Enemy-family atlas + reskin candidates | candidates open |
| S11 | Architecture atlas, 12 module docs | landed |
| S12 | `tools/patch_sentinel.py`, advisory CI job | landed |
| S13 | Verified exploit ledger, 71 lines / 14 families | **SAT 2026-08-06** (R109–R111) |
| S14 | Non-card parity sweep, 173 entities → NC-1…NC-20 | **open — canonicity rulings owed** |
| S15 | Suite-hardening sweep, 111 pins | landed; pin-table paperwork one-liner open |

---

## 8. `X<n>` — S13 exploit mechanism families

All fourteen carry a disposition (R109/R110/R111). Verbatim verdicts live in
`review/redteam/exploit-ledger.md`; routings in `docs/dockets/`.

| Family | Mechanism | Disposition |
|---|---|---|
| X1 | Companion cost-delta accumulator | NOTE → Klee rework docket · **FLAG-1** |
| X2 | Self-replacing 0-cost companions | NEW LAW (cycling gated ≥ Uncommon) + audit (`TT-T1`) |
| X3 | Encore Performance self-closure | RATIFIED CHANGE (`SW2-S-1`) · **FLAG-2** |
| X4 | Guest Cast unfiltered ×1.5 | WATCH ITEM |
| X5 | Fanfare floor stacking, decay-proof | **HELD — FLAG-3** |
| X6 | Salon displacement double-pay | WATCH ITEM |
| X7 | Klee spark economy | NEW LAW (spark gate) + audit (`TT-T2`) |
| X8 | Bomb damage, two uncapped terms | AUDIT (`TT-T3`) |
| X9 | Kokomi charge bank | NOTE → Kokomi workshop docket |
| X10 | Metallicize treadmill | **CANDIDATE, not ratified** → companion-pricing docket |
| X11 | `replay_next_companion` stacking | RATIFIED CHANGE (`SW2-S-2`) |
| X12 | Cross-element reaction splashes | WATCH ITEM (blocked on O-1, now repaired) |
| X13 | 14-relic weakness eraser | NO ACTION |
| X14 | Structural softlocks | leg (b) RATIFIED (`SW2-S-3`) · ~~legs (a)/(c) **FLAG-4**~~ **leg (c) RULED INTENDED (R114), leg (a)'s root STAGED as `AB-s2`** |

> **All fourteen dispositions are now final or queued (R114, 2026-08-06).** The
> four HELD flags are discharged; `X5` is the only family whose pin changed
> polarity, because it is the only one ruled *intended*. `X1`, `X3` and `X14`
> queue fixes to Errata Batch 2 and keep their `xfail(strict)` markers, since a
> ruling is not a fix.

---

## 9. `NC-<n>` and `SYS-<n>` — parity sweep findings

- **`SYS-1` … `SYS-14`** — S1 card-parity systemic families,
  `review/parity-sweep/triage-memo.md`. 41 distinct defects behind them.
- **`NC-1` … `NC-20`** — S14 non-card parity families,
  `review/parity-sweep/noncard-triage-memo.md`. 174 findings across 173
  entities. ~~`NC-1`, shop slot 1 (`NC-10`), Frozen (`NC-7`) and `spend_potion`
  (`NC-8`) are the four canonicity rulings owed by [USER].~~
  **RULED 2026-08-06 (R116): five of them, not four.** `NC-1` sim canonical
  (companions scale with the player); `NC-7` each engine adopts the other's
  half; `NC-10` both engines defective against a stated slot spec; `NC-8` ruled
  by inclusion in the batch; and **`NC-11`**, minted as a *new* question by the
  fourth sitting (because `NC-1` was ruled and explicitly did not cover it) and
  ruled by the final dispatch — power-sourced block stays **raw**, sim
  canonical. **The standing register the pair creates:** power-sourced *damage*
  runs the damage pipeline (`NC-1`); power-sourced *block* is raw (`NC-11`).
  All five fixes are Errata Batch 2 items and none is written. The rest of the
  triage is untouched.

---

## 10. House Lights finding ids

| Namespace | Meaning | Document |
|---|---|---|
| `N-1` | Track N lore audit's top finding (`gorget` / Concealed Unguis provenance). Docketed by R112. | `docs/lore-fidelity-audit-2026-08-05.md` |
| `LF-G1`…`LF-G5` | Track N coverage gaps in `lint_furina_registers.py` | same |
| `O-1` | Track O's top finding — the gauntlet stage-merge denominator defect. **REPAIRED** by Track U (R112). | `docs/instrument-redteam-2026-08-05.md` |
| `O1-1`…`O12-n` | Track O per-slice findings; the digit before the dash is the slice | same |
| `T-1`, `T-2`, `T-3` | Track T audit sweeps → `TT-T1/2/3` | `docs/track-t-audits-2026-08-06.md` |

---

## 11. `A<n>` — the seven scorecard axes

A1–A7 are the axis namespace. Live law is `tier0/harness/axes.py`; the historical
definitions are `docs/archive/tier0-simulator-spec.md` §6. Since `DEC-D3` the axis
numbers are **reportable but NOT load-bearing** until `B-G1` rules.

Beware the two non-axis `A`-tokens listed in §2.9: Klee pass-4 asks **A3/A5**
and the **A0** co-op smoke run.

---

## 12. Track letters and batch code-names

**Track letters are reused by every batch and mean nothing on their own.**
`Track B` has meant at least four different things. Always write
`<batch> Track <letter>`.

| Batch / sprint code-name | When | Track letters used |
|---|---|---|
| Serenitea Sweep | 2026-07-26 | A–G |
| Serenitea Sweep II | 2026-07-27 | A–E, D1 |
| Curtain Call → "Take a Bow" | 2026-07-27 | A–C, gates `CC-G1/G2` |
| Ship What We Know | 2026-07-25 | A–F, gates `G-<track><n>` |
| Neap Tide | 2026-07-26 | B, E, F batches; items `NT-G<n>`; predictions `NT-P<n>` |
| EPOCH 1 / EPOCH 2 | 2026-07-26 | — |
| Animation sprint 1 / 2 | 2026-07-23 / 24 | A–G (sprint 2) |
| Axis-Validity session | 2026-08-04 | A, B, C; gates `A-G1`, `B-G1`, `AV-G2` |
| Understudy | 2026-08-04 → | phases `UND-P0/P1/P1.5/P2` |
| Surplus Week | 2026-08-05 | streams `SW-S1…S15` |
| Last Call / House Lights | 2026-08-05 | A–P (G roster anchor, H reactions, I captures, J dossiers, K mutation, L sitting pack, M Downfall, N lore, O instrument, P probe-d) |
| Second Wind | 2026-08-06 | R (sitting), S (errata `SW2-S-1…3`), T (audits `TT-T1…3`), U (O-1 repair), W (replies) |
| Strike the Set | 2026-08-06 | S, T, U, W, **X (this registry)** |
| Empty the Green Room | 2026-08-06 | Y (answers landing), Z (docs diet) |
| Cold Reading | 2026-08-06 | AA (R102 escrow), AB (flag resolutions; staged `AB-s1`/`AB-s2`), AC (fork, gates, S14 canonicity) |

---

## 13. Coverage, and what this registry deliberately does not do

**Swept:** `docs/**` (incl. `archive/`, `dockets/`, `pending/`, `atlas/`),
`review/**`, `tier0/DECISIONS.md`, `klee-mod/DECISIONS.md`, `tools/**`,
`tier0/**`, `tier05/**`, `understudy/**`, `klee-mod/**/*.cs`, root `README.md`,
`.github/workflows/repo.yml`, `.gitignore`.

**Not enumerated, on purpose:**

1. **Every `<Letter><n>` task-id in every sprint plan.** Several hundred, all
   document-scoped; §2.9 states the rule instead and lists the escapees.
2. **R1–R38.** They cannot be resolved mechanically from the paper (S4 §4 lead
   3). Carried as an open item in the queue rather than guessed.
3. **Card, relic, power and companion ids** (`sayu_naptime`, `crowd_work`, …).
   Those are content keys with a single home in `docs/*.yaml`; they are not an
   identifier namespace with a collision problem.
4. **Section numbers** (`§4.7`, `§10.11`). Scoped to their document by
   construction.

**Anything this registry could only have filled in by inventing a fact** was
routed to `docs/registry/user-queue.md` §4 (AWAITING) instead of guessed.

---

## 14. Keeping this file true

`tools/lint_identifier_registry.py` (CI, job `lints`) checks **additions, not
the corpus**: every identifier present today is grandfathered by the committed
snapshot `docs/registry/known-identifiers.tsv`. It fails only when

- a **new** identifier appears in a tracked namespace and is not in this file; or
- a **new document** uses a bare `G<n>` whose number is minted by two or more
  namespaces in §2.1, instead of the qualified form.

Both are escapable — add the row, or use the qualified form. The escape hatch
for a deliberate bare use is the marker `identifier-registry: allow-bare`
anywhere in the file. Refresh the snapshot with
`python tools/lint_identifier_registry.py --update-baseline`.

A third rule, added 2026-08-06 by the docs diet (Track Z), fails a **new**
document that mints an open-item row outside the queue and the dockets. See
§16.

---

## 15. Lifecycle status index — LIVING / REFERENCE / ARCHIVED

Opened 2026-08-06 by the docs diet (Track Z). **Zero design authority**, like
the rest of this file: a status says how a document is *maintained*, never
whether its contents are true or ratified.

**The three statuses.**

| Status | Meaning | What you do with it |
|---|---|---|
| **LIVING** | Expected to change. Must be read to work on the project. | Read it. Keep it true. |
| **REFERENCE** | A frozen record — sprint logs, countersign packages, playtest records, research harvests, retired registers. | Read it when something cites it. Do not maintain it; corrections land in the superseding doc. |
| **ARCHIVED** | Superseded. Kept verbatim as a record, never updated. Lives in `docs/archive/`. | Read it only for history. |

Every `.md` and `.yaml` file under `docs/` carries its status as a header line
(a blockquote in Markdown, a leading `#` comment in YAML). Eighteen files
cannot carry one and are indexed here instead — see "Index-only" below.

### 15.1 Counts (2026-08-06, after the diet)

| Status | Files |
|---|---|
| LIVING | 59 |
| REFERENCE | 205 |
| ARCHIVED | 66 |
| **total under `docs/`** | **330** |

### 15.2 The LIVING set, in full

The living-doc budget (Track Z, Z-2) is: the two DECISIONS ledgers (outside
`docs/`), the design principles, the registry pair, `docs/dockets/`, the
card/upgrade/companion sheets, and at most one charter per active sprint.
Everything below beyond that budget is an **exception**, and its reason is in
the same row.

| File | In budget? | Why it is LIVING |
|---|---|---|
| `teyvat-spire-design-principles.md` | budget | the design constitution |
| `registry/identifiers.md`, `registry/user-queue.md` | budget | the resolver and the open-item register |
| `registry/known-identifiers.tsv` | budget | the lint's grandfathering snapshot; regenerated, never frozen |
| `dockets/README.md`, `dockets/klee-rework.md`, `dockets/kokomi-workshop.md`, `dockets/companion-pricing.md`, `dockets/watch-items.md`, `dockets/engineering-backlog.md` | budget | routed-not-decided inboxes; one of the two places an open item may live |
| `furina-cards.yaml`, `furina-upgrades.yaml`, `klee-cards.yaml`, `klee-upgrades.yaml`, `kokomi-cards.yaml`, `kokomi-upgrades.yaml`, `fontaine-companions.yaml`, `inazuma-companions.yaml`, `mondstadt-companions.yaml`, `ref-ironclad-upgrades.yaml` | budget | the design sheets; read directly by both sims and by codegen |
| `axis-validity-session-charter.md` | budget | the one charter of the open Axis-Validity sprint |
| `understudy-kickoff-brief.md` | budget | the one charter of the open Understudy sprint |
| `animation-sprint-2-plan.md` | budget | the one charter of the open animation sprint |
| `README.md` | **exception** | the docs index; a stale index is worse than no index |
| `atlas/` (14 files) | **exception** | the code map — each file tracks a live module and changes when that module does |
| `awaiting-user-slots-2026-08-06.md` | **exception** | holds the pre-drafted landing text for slots 4/6/7 ~~, which are still AWAITING~~ — **all landed 2026-08-06 (wave 8, R118)**; kept LIVING as the slot record until a future diet freezes it |
| `class-p-charter-2026-08-06.md`, `clear-the-stage-charter-2026-08-06.md` | budget | the charters of the two SIGNED operating protocols (R119); LIVING while their swarms operate, per their own lifecycle headers |
| `kokomi-playtest-protocol.md` | **exception** | its "Answers" block is filled at the table; `OT-1` was added to it on 2026-08-06 |
| `klee-character-design.md`, `furina-kickoff-v0.1.md`, `kokomi-kickoff-v1.md` | **exception** | identity charters, amended in place; they are law for their character in the way the principles doc is law for the project |
| `art-asset-manifest.md`, `furina-art-pass-requirements.md`, `kokomi-art-pass-requirements.md` | **exception** | art bills maintained "AS SHIPPED"; they are the current state of the art surface, not a record of a pass |
| `art-sprint-spec.md` | **exception** | the art-pipeline regime the art lints enforce; changing the regime means changing this file |
| `roster-codegen.md`, `upgrade-conventions.md` | **exception** | build-path and grammar references maintained in place; both carry dated correction notes rather than being superseded |
| `patch-sentinel.md` | **exception** | describes a surface that changes with every base-game patch |
| `worktree-workflow.md` | **exception** | the canonical statement of the worktree policy (`SS-G4`); Z-6 points three other sites at it |
| `role-tempo-floors.yaml`, `role-tempo-debt.tsv`, `role-tempo-review.tsv`, `track-b-curves.md` | **exception** | generated or machine-read instrument data; they regenerate rather than freeze |
| `art-claimed-sources.tsv`, `reserved-card-names.txt`, `card_keywords.json`, `noncard-parity-vectors.json`, `furina-fanfare-parity-vectors.json`, `s7-divergences.tsv` | **exception** | machine-read data files, rewritten by their producers |

### 15.3 REFERENCE — by class

Nothing in this class is maintained. If one of them contradicts a LIVING
document, the LIVING document wins and the contradiction is a defect in the
LIVING one, not in the record.

| Class | Count | Where |
|---|---|---|
| Enemy dossiers | 112 | `docs/enemy-dossiers/` (+ `fight-class-labels.yaml`) |
| Completed sprint logs, plans and reports | 42 | `docs/sprint-*.md`, `docs/*-sprint-log-*.md`, `docs/*-sprint-plan.md` |
| Countersign packages and gate records | 6 | `axis-validity-countersign-2026-08-04.md`, `understudy-countersign-2026-08-04.md`, `track-b-validation-gate-countersign-2026-08-04.md`, `a2-gate-ratification-2026-07-27.md`, `handback-note-2026-08-04.md`, `sitting-record-predraft-2026-08-06.md` |
| Playtest records and triage | 6 | `playtest2-triage-*`, `playtest3-notes-*`, `playtest4-notes-*`, `playtest4-triage-*`, `g12-review-*`, `punch-off-crash-memo.md` |
| Probe registrations (unsigned, awaiting countersign) | 4 | `probe-a-block-offset.md`, `probe-b-fanfare-residual.md`, `probe-d-registration-draft.md`, `probe-e-corpse-detonation-registration-draft.md` — **probes (d) and (e) COUNTERSIGNED 2026-08-06 (10.13 / R120 and Q11 / R118); both runs are owed, Track M** |
| [USER] dispatch records (wave 8) | 3 | `dispatch-2026-08-06-q13-q14-q15.md`, `dispatch-2026-08-06b-eleven-replies.md`, `dispatch-2026-08-06d-four-replies.md` — the verbatim ruling dispatches R117/R118/R120 execute |
| Research harvests and audits | 12 | `act2-act3-roster-research.md`, `sts2-map-and-events-research.md`, `sts2-events-harvest.txt`, `companion-value-vs-colorless-study.md`, `lore-fidelity-audit-2026-08-05.md`, `instrument-redteam-2026-08-05.md`, `reactions-corpus-*`, `s7-*`, `zhongli-dossier-*`, `slot5-candidates-*` |
| Retired open-item registers (Z-3) | 5 | `backlog-2026-07-29.md`, `open-playtest-items.md`, `missed-requirements.md`, `sitting-prep-2026-08-05.md`, `surplus-week-manifest-2026-08-05.md` |
| Adopted proposals, retained | 3 | `pending/` |
| Everything else | 15 | briefs, memos, design notes, calibration records |

### 15.4 ARCHIVED

All 66 live in `docs/archive/` and were archived before this diet. The archive
map — one line per document, saying why it closed and where its live successor
is — is `docs/README.md` § "Archive map". **The docs diet moved nothing new
into the archive**, and the reason is worth recording so the pass is not re-run
blind: every file under `docs/` is cited by at least one live artifact, test,
tool or ledger, so archiving any of them would have broken a citation to fix a
status. REFERENCE-in-place gives the same reader benefit at zero citation cost.

**The citation guarantee that makes REFERENCE safe.** A frozen document does
not move. 37 distinct `docs/` paths are cited from `tools/` — four modules cite
`docs/track-a-kickoff-brief.md` alone, which is why the 2026-08-06 archive
review kept it live. `tier0/tests/test_doc_citation_targets.py` now fails if
any of those 37 stops resolving, so the next paper pass that renames a
citation target finds out from the suite rather than from a broken tool.

### 15.5 Index-only files (18)

These carry no header, either because the format has no comment syntax that
their readers tolerate, or because a generator would overwrite it. Their status
lives here and nowhere else.

| File | Status | Why index-only |
|---|---|---|
| `registry/known-identifiers.tsv` | LIVING | generated TSV |
| `role-tempo-debt.tsv`, `role-tempo-review.tsv`, `s7-divergences.tsv` | LIVING | machine-read TSV |
| `art-claimed-sources.tsv` | LIVING | machine-read TSV |
| `reserved-card-names.txt` | LIVING | machine-read list |
| `card_keywords.json`, `noncard-parity-vectors.json`, `furina-fanfare-parity-vectors.json` | LIVING | JSON has no comments |
| `role-tempo-floors.yaml`, `role-tempo-baseline.md`, `role-tempo-tagthrough.md`, `track-b-curves.md` | LIVING (floors, curves) / REFERENCE (baseline, tagthrough) | fully machine-generated; a header would be overwritten on the next rebuild |
| `reactions-corpus-battery-2026-08-05.tsv`, `-corrected.tsv`, `reactions-corpus-cohort-2026-08-05.tsv` | REFERENCE | machine-read TSV |
| `sts2-events-harvest.txt` | REFERENCE | raw harvest |
| `animation-sprint-1-a4-gate.png` | REFERENCE | image |

---

## 16. Where an open item may live — and the lint that keeps it there

Opened 2026-08-06 by the docs diet (Track Z, Z-3). Before it, "what is open"
was spread across at least eight registers; five of them are now REFERENCE
husks whose still-open rows were migrated verbatim.

**The rule, stated once.** An open item lives in exactly one of two places:

1. **`docs/registry/user-queue.md`** — anything that needs [USER]: a reply, a
   ruling, a countersign, a taste pick, or time at the table.
2. **`docs/dockets/`** — anything routed and not decided, including
   `dockets/engineering-backlog.md`, which owns open *engineering* work that
   needs no ruling to start.

Any other document may *describe* an open item at length — that is what the
"Full text" column of the queue points at — but the row that says **"this is
open"** lives in the queue or a docket, so that "what is open" has one answer.

**The lint.** `tools/lint_identifier_registry.py` RULE 3 fails a **new**
document (one absent from the grandfathering snapshot) that mints an open-item
row outside those two homes. Like RULES 1 and 2 it is diff-shaped: the existing
corpus is grandfathered and never fights it. Two escape hatches, both cheap:

- give the document the **REFERENCE** or **ARCHIVED** lifecycle header — a
  frozen record is allowed to restate the history of an item; or
- add the marker `open-items: allow-elsewhere` anywhere in the file.
