# Combined digest — inventory phase (Strike the Paperwork + Clear the Stage)

> **Lifecycle: REFERENCE** — the inventory-phase section of the one-page
> digest both charters require. The execution sections (what actually landed,
> revert handles) are P-B/P-C's and R-E's to append after the v6 window
> closes. Nothing described below has been acted on.

**What this was.** Both signed charters (R119) share one inventory pass: map
who cites whom across the whole paper trail, sweep the queue and backlog for
five-test paperwork items, and plan the docs cleanup — without touching
anything. That pass ran on 2026-08-06. Everything it produced is in
`review/stage-clear/`; nothing else changed.

**What was found, in plain terms:**

- **The citation map exists now.** 2,227 citations across 655 files, checked
  against the existing suite test (all 37 of its pinned paths reconcile).
  27 cited paths point at nothing; most are old archive files pointing at
  each other from before their moves (harmless, tolerated), but two were
  worth flagging: a live test cites a document that has never been in the
  repo, and the code atlas uses a shorthand path that resolves to nothing.
- **Paperwork candidates: 7 PASS, 1 sequenced, 4 DOUBT.** Seven items pass
  all five tests with no doubt and are written up ready for the execution
  swarm: keep the sentinel's relic spelling (10.4), confirm which replay
  module the acceptance clause meant (10.5), reclassify the Punch Off crash
  as game-side (10.6), authorize the §2.2a citation repair (10.9), fix the
  atlas shorthand, fix the phantom-document citation in the test, and correct
  a one-word stale range in the identifier registry. One more (the four-card
  measurement-cell confirm) is clean on four tests but waits for the v6
  measurement window to close. Four are DOUBT and stay put — including one of
  the charter's own seeds (the catalyst-Kokomi watchlist confirm), where
  re-checking found the "missed listing" premise unclear rather than
  mechanical. When in doubt, it stayed a queue row.
- **Demotion list: 17 files can move today, 87 eventually.** Of 112 docs at
  the root, 87 are frozen records. 17 have no live citers at all and can move
  to the archive immediately. Most of the rest are only cited by the index
  files, which the move commit repoints. The one real policy question: 36 of
  them are cited by the append-only decision ledgers, whose text we never
  edit — moving those files permanently stales a ledger line, so that set is
  held for your call. The ≤15-file target is reachable, but only through
  that question.
- **Prune candidates: 6 certified, 5 held as DOUBT.** Six sections in living
  documents are provably superseded by a named ruling (mostly the answered
  queue rows and the discharged held-flags tables); each cites its
  superseder. Five more look stale but could not be certified without a
  judgment, so they are listed as questions, not cuts.
- **Ledger volumization (R-D), planned:** freeze R39–R99 into an archive
  volume, keep R100+ live, generate the current-law digest from a small
  status table that gets one red-pen pass, leave the Klee ledger whole for
  now (its open entries are interleaved with history). Registry and CI
  changes specified; the cross-session note is drafted and posts before
  anything moves.

**Vacation-test summary:** we counted everything, touched nothing, and the
whole cleanup now has a written order of operations. Seven small paper fixes
are ready to land the moment the execution swarm is unfrozen; one question
(may files cited by the decision ledgers move?) is yours before the big
tidy-up can finish.
