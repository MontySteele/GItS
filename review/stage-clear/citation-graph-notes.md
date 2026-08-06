# Citation graph — extraction rules, blind spots, reconciliation (R-A / P-A, wave 8)

> **Lifecycle: REFERENCE** — findings record of the shared inventory pass
> (Class-P charter track P-A + Clear the Stage track R-A, both SIGNED per R119).
> Surfacing only: nothing outside `review/stage-clear/` was changed by this pass.

**Producer:** `review/stage-clear/extract_citations.py` (run from repo root).
**Outputs:** `citation-graph.tsv` (one row per (citer, cited) edge) and
`citation-indegree.tsv` (one row per file in `docs/` and `review/`, including
zero-in-degree files, with citer counts split by citer class).
`_rb_table.py` post-processes the two TSVs into the bucket table used by
`refactor-plan.md` §R-B.

## Headline numbers (2026-08-06, at 745139b)

| Measure | Value |
|---|---|
| Edges (citer → cited) | **2,227** |
| Citing files scanned | 655 |
| Distinct cited targets | 393 |
| Dead citations (cited path not on disk) | **27 targets** |
| Pin-test reconciliation (`test_doc_citation_targets.py`) | **37 / 37 in graph, 0 missing** |

## Extraction rules

Citing scope: every `.md/.py/.yaml/.yml/.txt/.tsv/.json/.toml/.cfg/.ini` file
under `docs/`, `review/`, `tools/`, `tier0/tests/`, `tier05/tests/`,
`understudy/`, plus `tier0/DECISIONS.md` and `klee-mod/DECISIONS.md`.
`review/stage-clear/` itself is excluded (this pass must not cite itself into
its own graph). Cited scope: paths into `docs/` or `review/`.

1. **Path rule** — regex `(?<![A-Za-z0-9_/.-])(docs|review)/…\.(md|yaml|yml|tsv|json|txt|png|html)`.
   The lookbehind stops `vendor/STS2_MCP/docs/raw-simplified.md` from matching
   as `docs/raw-simplified.md` (a real false positive caught during
   development; two residual shorthand citations in
   `docs/atlas/vendor-sts2-mcp.md` genuinely spell the bare `docs/…` form and
   stay in the graph as dead — see candidate C-7).
2. **Wiki rule** — `[[name]]` resolved through the basename index. (Zero hits
   in practice; the repo does not use wiki links.)
3. **Bare-name rule** — a bare filename mention (e.g. `` `backlog-2026-07-29.md` ``)
   resolves to its `docs/`+`review/` owner **only if the basename is unique**
   across both trees. Exactly two basenames are ambiguous and excluded:
   `README.md` and `gallery.md`. Markdown relative links are caught by this
   rule where the basename is unique.

Each edge is deduplicated per (citer, cited); the `rule` column records which
rule fired first (path > wiki > bare). Citer class in the indegree table:
`CODE` (tools/tests/understudy), `LEDGER` (the two DECISIONS files —
append-only, so their citations can never be repointed), `LIVING` /
`REFERENCE` / `ARCHIVED` (from the file's own Z-1 lifecycle banner;
`docs/archive/` implies ARCHIVED), `REVIEW` (review/ artifacts, mostly
frozen findings), `UNBANNERED` (no banner found — five root files, of which
three are §15.5 index-only generated files, one carries a deliberate
`Lifecycle: DRAFT` banner outside the three-status vocabulary, and one has no
banner at all; see candidates C-10 and the blind-spot list).

## Known blind spots (read before quoting the graph)

- **R-number citations are invisible.** `R107(a)`-style citations into the
  ledgers are how most law is actually cited; this graph only sees
  path-shaped/filename references. Ledger in-degree here badly understates
  real ledger usage — the R-D volumization plan must NOT read the graph as
  "few things cite DECISIONS".
- **Prose references are invisible** ("the fanfare sprint log", "the parity
  memo"). In-degree is a floor, not a truth. The diet's own finding — all 218
  non-dossier files had live inbound citations under a wider notion of
  reference — is not contradicted by zero rows here.
- **Section-level anchors are not modelled.** An edge says "file cites file",
  never which section; R-C prune work must re-check the citing line by hand.
- **CLI-example output paths count as citations.** `understudy/replay.py:78`
  shows `--ledger docs/probe-b-ledger.tsv` in a usage example; the file is an
  output the command would create, not a missing document. It is the one
  known edge of this class; treated as a false positive, not a defect.
- **Forward references count as dead.** The two charters cite
  `docs/registry/p-ledger.md` and `docs/registry/excision-log.md`, which the
  execution swarm (P-B / R-C) will create. Dead in the mechanical sense only.
- **Gitignored/never-committed targets read as dead.** `docs/mockups/…html`
  is gitignored (exists only on the primary machine, if at all); two `.png`
  contact sheets were never committed. The graph cannot tell "lost" from
  "deliberately untracked".
- **Ambiguous basenames** (`README.md`, `gallery.md`) are never matched by the
  bare-name rule, so e.g. "see gallery.md" prose mentions produce no edge.
- **Same-file self-citations are dropped**, as are edges from
  `review/stage-clear/` itself.

## Reconciliation against `tier0/tests/test_doc_citation_targets.py`

That test pins the 37 distinct `docs/` paths cited from `tools/*.py`
(existence-only, Z-4). Re-deriving the 37 with the test's own regex and
comparing against this graph's `tools/ → docs/` path-rule edges: **all 37
present, none missing, no extras unaccounted**. The flagged case
(`docs/track-a-kickoff-brief.md`, ≥4 tool citers) appears in the graph with 4
tool citers plus `docs/README.md` and `docs/registry/identifiers.md`.

Note the test's deliberate narrowness, now visible mechanically: it sweeps
**tools/ only**. `tier0/tests/test_card_play_hook_guards.py` cites
`docs/coop-no-sim-backstop.md`, which has never existed in the repo, and no
lint catches it because the citer is a test, not a tool (see candidate C-8;
the Q15 WIDEN ruling that Track V is executing widens the *citation lint* to
`tools/*.py`, which still does not reach `tier0/tests/`).

## The 27 dead citations, classified

| Class | Count | Disposition |
|---|---|---|
| Archive-internal sibling pointers — `docs/archive/*` citing a sibling's pre-move root path | 18 targets | Frozen citers (rail 1: never edit REFERENCE/ARCHIVED text). Tolerated staleness, long-standing precedent. Candidate C-11 (DOUBT) records the policy question for R-B. |
| Never-existed doc cited by live code + 2 frozen docs (`docs/coop-no-sim-backstop.md`) | 1 | Candidate **C-8** (PASS): repair the test docstring; frozen citers stay. |
| Atlas shorthand for vendor paths (`docs/raw-full.md`, `docs/raw-simplified.md` in `docs/atlas/vendor-sts2-mcp.md`) | 2 | Candidate **C-7** (PASS): LIVING doc, spell the full `vendor/STS2_MCP/docs/…` path it uses elsewhere. |
| Charter forward references (`p-ledger.md`, `excision-log.md`) | 2 | Not defects; created by the execution swarm. |
| Gitignored / never-committed binaries and mockups (`animation-sprint-2-a3-intake.png`, `klee-art-hunt-contactsheet.png`, `docs/mockups/salon-stage-d1-mockup-2026-07-28.html`) | 3 | Citers frozen; whether the PNGs should have been committed is surfaced as C-12 (DOUBT), not repaired. |
| CLI output-path example (`docs/probe-b-ledger.tsv`) | 1 | False positive of the extractor; no action. |

## Three biggest surprises

1. **A live test cites a document that was never in the repo.**
   `tier0/tests/test_card_play_hook_guards.py:13` cites
   `docs/coop-no-sim-backstop.md` — the name of a chat-memory topic, not a
   repo file (two frozen docs repeat it). The citation-existence gate never
   saw it because it sweeps `tools/` only.
2. **The ≤15-root-files target is an index-repointing job, not a breakage
   risk — except for the ledgers.** Of 87 REFERENCE files at `docs/` root,
   only 17 are cited by nothing live; but the live citers of the other 70 are
   overwhelmingly the index layer itself (`docs/README.md`,
   `registry/identifiers.md`, `registry/user-queue.md`, the dockets) plus a
   modest set of tool/test docstrings — all repointable in the move commit.
   The un-repointable citers are the two **append-only DECISIONS ledgers**
   (path-shaped citations to ~40 docs); any move of a ledger-cited file
   permanently stales a ledger line. That single fact should drive the R-B
   move policy (see refactor-plan §R-B, rule M3).
3. **Frozen-paper staleness is already the norm, not the exception.** The
   pre-diet archive carries 18 dead sibling pointers from its own earlier
   moves, tolerated for weeks without harm — evidence that "move whole,
   accept stale pointers inside frozen records, keep the index true" is a
   workable regime, and that the citation *suite gate* (which checks only
   live surfaces) is the right instrument rather than a full-graph gate.
