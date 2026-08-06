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

---

## P-B — execution (appended 2026-08-06; the window closed, the swarm ran)

**What landed: the seven ready fixes, each its own commit so each can be
vetoed alone.** Flag any one and it reverts by its handle, no argument. Full
attestations: `docs/registry/p-ledger.md`.

1. **Kept the sentinel's relic spelling** and closed the question — the name
   was accurate all along, and renaming it would have invented three false
   alarms. (`2489d26`)
2. **Confirmed which replay module the old acceptance clause meant** — the
   one that compares recordings, exactly as the sprint record's own evidence
   said. Nothing in either module changed. (`b6e8549`)
3. **Reclassified the Punch Off crash as the base game's**, not ours — the
   memo proved our code contains no signal connections at all. The watch
   stays; the caveat about the rotated-out crash log is preserved.
   (`d558264`)
4. **Fixed the stun-rule's citation** in the design principles — it cited a
   card that doesn't exist; it now cites the census showing the official pool
   has no player stun anywhere, which supports the rule *better*. The rule
   itself: untouched. Also opened the excision log the refactor charter
   requires. (`e52fae2`)
5. **Spelled out five broken shorthand paths** in the code atlas (the
   inventory said six; the sweep found five — one line held two). (`32163cf`)
6. **Repointed one live test's citation** from a document that never existed
   to the real in-repo statement of the same fact. (`ce85d34`)
7. **Corrected one stale number** in the identifier registry's prose (the
   ruling range now says R120, matching its own table). (`9907f3b`)

**Plus the charter's bookkeeping:** the P-ledger itself, and a new lint that
fails the suite if a ledger row ever lacks its five-line attestation or if
any ledger commit touched a file your gates own (`tools/lint_p_ledger.py`,
wired into CI like the other lints).

**What stayed, and why (nothing here was acted on):**

- **The four-card measurement cell (M12a)** — held for the window, then
  **downgraded on re-check**: the ratified card sheet itself says two of the
  four cards have since *left* that cell, so the record disagrees with itself
  (three vs four vs two). Reconciling that is a judgment, so it stayed on
  your queue with the conflict written out.
- **The catalyst-Kokomi watchlist confirm (M12b)** — the premise turned out
  false: she *was* registered, in two places. Recorded as a finding; nothing
  needed doing.
- **An unbannered findings doc** — choosing its lifecycle status is the
  judgment; docketed for the animation track (`EB-44`).
- **18 dead cross-references inside the archive** — unfixable without editing
  frozen text; recorded as a policy input for the upcoming doc-move track
  (`EB-45`).
- **Two screenshots cited but never committed** — only your machine knows if
  they still exist; one line added to the awaiting-facts list.

**Vacation-test summary of the batch:** seven paper fixes landed, each
individually revertable by one word from you; five things that looked like
paperwork turned out to need a person and are parked where you'll find them.
No number, card, behaviour, or law moved.

---

## R-B — execution (appended 2026-08-06; REFERENCE demotion, the big move)

**What landed: 44 frozen records moved out of the docs root into the
archive, verbatim.** Every moved file keeps every byte it had, under a dated
banner naming its old path, new path and this track. Every live citer — the
index files, the registries, the queue, the dockets, tools, tests, the
understudy harness, even comments in the mod's C# and the tier-0.5 content
YAMLs — was repointed in the same commit as its move, so nothing live points
at a gap. The per-file map (what moved, who was repointed, which frozen
pointers were knowingly left stale) is `rb-move-manifest.tsv`.

**Counts.** Root `docs/*.md`: **116 before, 72 after.** Moves by bucket:
17 with no live citers at all (bucket A), 11 cited by code (bucket C, code
repointed and smoke-run), 16 cited only by index-layer documents (bucket D).
The citation pin test, both suites and all lints are green at every batch
boundary.

**The gap, stated plainly: the root cannot reach the charter's 15 files
without you.** 45 of the remaining frozen records are cited by the
append-only decision ledgers, whose text is never edited — moving any of
them breaks a spine citation permanently. All 45 stayed put, and the policy
question is now **queue row Q20**: either the registry gains a resolver
table that maps old paths to new ones (ledger text stays verbatim, the move
proceeds), or ledger-cited records stay at the root and the 15-file target
is formally amended. Your call; R-B took neither.

**Also deliberately not moved, though nothing blocked them mechanically:**
`track-a-kickoff-brief.md` (an earlier pass chose freeze-over-move for
exactly this file and pinned its path in a named test) and
`roster-anchor-v14-v6-2026-08-06.md` (THE quotable standing table).

**Vacation-test summary:** forty-four frozen records changed address and
nothing else; every live pointer follows them; the one question a move pass
cannot answer alone is written on your queue as Q20.
