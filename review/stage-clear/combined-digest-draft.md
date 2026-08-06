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

---

## R-C — the LIVING prune (2026-08-06)

**What was pruned (four cuts, five certified candidates, each its own
commit + excision-log row E-2…E-5):**

- **P-1** — `docs/awaiting-user-slots-2026-08-06.md` froze LIVING →
  REFERENCE, verbatim, no move. All seven slots are answered and landed
  (Track Y; `AC-2`/R115; Q7/Q9/Q10 per R118) and the file's own §15.2 row
  anticipated exactly this freeze. LIVING count 61 → 60. (E-2, `8983890`)
- **P-2** — the queue's §3 held-flags table (all four RULED, R114)
  collapsed to a pointer: verdicts at R114, struck record at identifiers
  §6, the law at dockets/README rule 3. (E-3, `9024d4f`)
- **P-3** — queue §1 rows `Q1`–`Q17`, all ANSWERED (R113–R120), compacted
  into the "Already answered" table — verbatim verdicts kept byte-for-byte,
  residuals named per row. Its sequencing condition (Tracks V/M landing)
  was re-verified against current main first: Track V's execution commit
  `0189e46` covers Q6/Q9/Q13/Q14/Q15/Q16, Track M closed the v6 window
  green. **One delegation could not be found landed** and is named on the
  compact Q10 row: Track V's surface-only verification of the X14 line's
  acquisition vector + the pin-docstring annotation — the task stays
  recorded verbatim on the exploit ledger's X14 leg-(a) line, which is its
  register. (E-5, `e673933`)
- **P-4** — identifiers §6's held-flag framing prose replaced by a
  one-line pointer (R114; the rule's home is dockets/README rule 3); the
  struck table stays as the record. (E-4, `9ed4f79`)
- **P-5** — nothing left to do: the §3 prose R-range figure was already
  corrected by Class-P (R119 / P-B item C-9, handle `9907f3b`); verified in
  place, not double-logged.
- **P-6** — not a prune by the plan's own words: the README index rows for
  R-B's moved files were repointed in the move commits; spot-checked (no
  stale root-path pointer in README/registries; the citation pin test
  guards it mechanically). No R-C action.

**What stayed, with the doubt named (all five DOUBT rows verified still
surfaced where the plan holds them, §R-C of
`review/stage-clear/refactor-plan.md`):** D-1 (axis charter's earlier
sections vs the R118 closure — needs a section-by-section read), D-2
(design-principles restatements Z-6 did not finish — each cut needs its own
citation), D-3 (character kickoffs — must NOT be pruned while queue rows
`M1`/`M2` are open; both rows confirmed open in queue §10), D-4 (art
manifest — an art-debt question, queue §8 confirmed carrying it), D-5
(§15.1's 330-file recount — a sequencing choice; R-B left a location note,
the recount is still owed once). None was touched.

**The acceptance gap, stated honestly.** The charter's R-C acceptance is
"no LIVING doc restates a ruling it can point to; excision log complete."
The six-candidate scope does not achieve that: this pass executed only what
the R-A inventory could certify with a named superseder, and the inventory
itself says it did not read all ~59 LIVING files section-by-section — that
reading remains the unexecuted bulk of R-C. A follow-up batch could
certify, in rough order of confidence: (a) the axis charter's superseded
gate prose once D-1's read is done against the landed R118 form; (b) the
principles-doc restatements (D-2) one ruling-citation at a time; (c) the
queue's own struck banners in §0/§4/§5 that restate discharged postures
each above a named ruling (same shape as P-2, not in this pass's certified
six); (d) the kickoffs — only after `M1`/`M2` are ruled. Also noticed en
route, surfaced not cut: the X14 pin docstring in
`tier0/tests/test_s13_exploit_pins.py` still reads "one word owed" for a
question R118 answered — that is Track V's still-owed annotation (named on
Q10's compact row), not an R-C cut.

---

## R-D — ledger volumization (appended 2026-08-06; the "million lines" move)

**What moved: the tier0 ledger's R39–R99 range — 2,943 lines — into
`tier0/DECISIONS-archive-R39-R99.md`, byte-identical below a dated volume
banner.** Verified mechanically at split time (the moved bytes compare equal),
and nothing inside any ruling changed: strikes, DRAFT markers and banners
travel with their rulings, including the interleaved D-series entries D2–D5.
The live `tier0/DECISIONS.md` (5,063 → 2,177 lines) keeps its header, the
pre-R39 prose record, and R100+, with a volume-pointer block and a
**generated current-law digest** where the range used to be. R1–R38 were
never headed entries anywhere; no entries were invented, and their back-index
question stays queue §4. **The Klee ledger was deliberately not split**, per
the plan: its still-operative prose entries (E2/E2b, the fork block) are
interleaved with history, and separating them would take exactly the
judgment calls this track is not allowed to make.

**The status sidecar, honestly: 5 derived, 77 UNREVIEWED.** One row per
ruling R39–R120 in `tier0/decisions-status.tsv`. The plan says statuses get
one [USER] red-pen pass; that pass has not happened, so no
operative/superseded judgment was authored. The five statuses recorded are
the mechanically derivable ones, each with quoted evidence: R54/R55 (R56's
preamble names their statline conclusions superseded), R56 (its own
SUPERSEDED-BY-R73 banner), R88 (the exclusivity clause struck per R118),
R102 (the escrow released and its banners struck per R113). The other 77
rows say UNREVIEWED, and the digest renders them as unreviewed — listed,
counted, and explicitly not judged. **The red-pen pass is now a queue row**
(`docs/registry/user-queue.md` §4, "Decisions-status sidecar red-pen").

**Every reader of the spine was taught the layout, and the notice posted
first.** Before the split commit: `docs/registry/ledger-layout-note-2026-08-06.md`
(the plan's drafted paragraph). In the same landing: the identifier registry's
§1/§3 now resolve every R-number to its volume by a mechanical rule (R39–R99 →
archive, R100+ → live) and §14 states the no-renumbering law; the citation
lint resolves against both tier0 volumes (its 41 clause citations — mostly
R90/R91, now archive-resident — still resolve); the P-ledger's gated-register
guard covers `DECISIONS*.md` so the archive is as write-protected as the live
file; the identifier lint scans and mines the archive; `tier0/harness/axes.py`'s
D3 citation and the docs README's spine row repointed. The CI duplicate-number
check graduated from an inline per-file script to `tools/lint_ledger_numbers.py`
— one R/D namespace across all volumes, with red-and-green tests — and a new
CI step fails the build if the generated digest goes stale or gets hand-edited.

**Vacation-test summary:** the spine's closed range changed address, byte
for byte, and every tool and index that reads it follows; the one thing that
would make the digest say "current law" — your red-pen pass over 77
unreviewed statuses — is written on your queue, not guessed at.
