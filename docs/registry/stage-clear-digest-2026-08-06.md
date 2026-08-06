# Stage-Clear digest — what the two R119 charters actually did (2026-08-06)

> **Lifecycle: REFERENCE** — the one-page combined digest both signed charters
> (Class-P purge §3 + "Clear the Stage" refactor, R119) require. Frozen as
> delivered; the objection window it opens is tracked in
> `docs/registry/user-queue.md`. Working draft it finalizes:
> `review/stage-clear/combined-digest-draft.md`. Status index:
> `docs/registry/identifiers.md` §15.

**Read this cold.** Two cleanup crews ran under the charters you signed at
R119: a paperwork purge (Class-P) and a docs refactor (Clear the Stage).
Nothing below changed a card, a number, a law, or game behaviour. Everything
below is individually revertable, and this page is the consent step: **any
row you flag reverts by its named handle, no argument (Class-P §3). Silence
ratifies the batch.**

## What landed

- **Seven paperwork fixes (P-B), each its own commit = its own veto handle**
  — full attestations in `docs/registry/p-ledger.md`: kept the sentinel's
  relic spelling (`2489d26`); confirmed the P1.5 clause meant the replay
  comparator (`b6e8549`); reclassified the Punch Off crash game-side
  (`d558264`); repaired §2.2a's phantom citation with the census (`e52fae2`);
  spelled the atlas's five vendor shorthand paths (`32163cf`); repointed one
  test's citation to a document that exists (`ce85d34`); corrected the
  registry's stale R-range word (`9907f3b`). Plus the bookkeeping the
  charters demand: the P-ledger, the excision log, and a lint
  (`tools/lint_p_ledger.py`) that fails CI if a ledger row lacks its
  attestation or a handle commit touches a [USER]-gated register — it
  passes today: *"7 row(s), all with five-line attestations; 7 handle
  commit(s) touch no [USER]-gated register."*
- **44 frozen records moved out of the docs root (R-B), verbatim** — each
  under a dated banner, every live citer repointed in the same commit.
  Root `docs/*.md`: 116 → 72. Per-file map (and the revert path — each move
  is one commit): `review/stage-clear/rb-move-manifest.tsv`. Spot-checked at
  acceptance: 5 random moves, banner present, content below the banner
  byte-identical to the pre-move blob.
- **Four prunes in living docs (R-C)** — the answered queue rows Q1–Q17
  compacted, the discharged held-flags table and its restatement collapsed to
  pointers, the slot file frozen. Every cut has a row in
  `docs/registry/excision-log.md` (E-2…E-5) naming its superseder and its
  revert commit; E-1 was P-B's citation repair.
- **The ledger split in two (R-D)** — R39–R99 (2,943 lines) moved
  byte-identical into `tier0/DECISIONS-archive-R39-R99.md`; the live spine
  went 5,063 → ~2,200 lines and gained a generated current-law digest. Every
  reader (lints, tools, tests, the registry) was taught the volume layout;
  CI now guards the R/D namespace across volumes and fails on a stale
  digest. Revert path: the split landed as its own commit pair
  (`2d0fab5` + `324a2df`); the notice posted first
  (`docs/registry/ledger-layout-note-2026-08-06.md`).

## What stayed, and why

- **M12(a), the four-card measurement cell** — failed the charter's own test
  4 on re-check: the record says three, four, and two cards at once.
  Reconciling it is a judgment; it stays on your queue (§10, `M12`).
- **The purge's doubt set** — M12(b) (premise false, recorded, nothing
  edited), the unbannered spike doc (`EB-44`), 18 archive-internal dead
  pointers (`EB-45`), two maybe-lost screenshots (queue §9). Doubt
  disqualifies; none was acted on.
- **R-C's five DOUBT rows** (axis-charter prose, principles restatements,
  character kickoffs behind `M1`/`M2`, the art manifest, the §15.1 recount)
  — held in `review/stage-clear/refactor-plan.md` §R-C, untouched.
- **45 ledger-cited files at the root (bucket B and friends)** — moving any
  of them permanently stales an append-only spine citation, so all stayed;
  that policy call is **Q20**, yours.
- **77 of 82 sidecar status rows say UNREVIEWED** — the ledger split's
  status table (`tier0/decisions-status.tsv`) records only the five
  mechanically derivable statuses; "still operative vs superseded" awaits
  your red-pen pass (queue §4).

## What is asked of you

1. **The objection window (Class-P §3), open as of this page:** skim the
   landed lists above; flag any row and it reverts by handle. Silence
   ratifies.
2. **The standing queue:** `Q18` (countersign the payoff-reach
   re-registration), `Q19` (accept or shield the anchor's tag side-effect),
   `Q20` (move policy for ledger-cited files), the decisions-status
   **red-pen pass** (queue §4), and the migrated `M`-rows (queue §10,
   `M12` now carrying its recorded conflict).

## The acceptance gaps, stated honestly

- **The root is 72 files, not the charter's ≤15.** The remainder is gated on
  Q20; no further move is possible without it.
- **R-C executed 4 cuts of 6 certified candidates out of ~59 LIVING files**
  — the section-by-section read of the living corpus is the unexecuted bulk
  of the prune charter; the follow-up order is written in the plan's §R-C.
- **The sidecar states no current law yet** — 77 UNREVIEWED rows render as
  unreviewed until the red-pen pass.

*Acceptance verification (Track R-E, 2026-08-06): before/after counts,
manifest spot-checks, excision-log and P-ledger reviews, full lint battery +
both suites green — recorded in the wave-8 close-out. Wave start commit
`07551fa` (root count then: 104; the 116 figure is R-B's own pre-flight
baseline after the wave's earlier landings).*
