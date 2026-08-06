> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/registration-hunt-report-2026-08-06.md` — new path: `docs/archive/registration-hunt-report-2026-08-06.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Registration hunt report — the payoff-reach / RARITY_ODDS pre-registration (queue row 10.7)

> **Lifecycle: REFERENCE once landed.** Track S2 of the wave-8 batch,
> 2026-08-06, branch `findings/track-s2-registration-hunt`, base `origin/main`
> = `07551fa`. **Read-only sweep**: nothing in any worktree was modified,
> cleaned, or deleted; no `game_ref` directory was entered.

**Authority:** [USER], verbatim (2026-08-06, queue row 10.7): *"Let's yes to
both and see if it turns up on local."* — (a) search-and-repair authorized,
local worktrees first; (b) `RA-G1`/`RA-G2` core-attainment columns
quarantined until the document is found or re-established.

## Verdict: NOT FOUND

The pre-registration document for the payoff-reach / `RARITY_ODDS` sprint does
not exist anywhere reachable on this machine: not in any branch, not in any
worktree's committed or uncommitted files, not in the stash, not among
unreachable git objects, not in the primary checkout's stray files, not in
session scratchpads, not in project memory. Consequences executed per the
authority:

- **Quarantine banner** added to `docs/roster-anchor-v14-2026-08-05.md`
  (the only committed document that publishes the `RA-G1`/`RA-G2`
  core-attainment columns). Numbers untouched; banner only (R101b).
- **Clean re-registration draft** written:
  `docs/payoff-reach-reregistration-draft-2026-08-06.md` — reconstructed
  strictly from committed citations, pinned to the current
  `DRAFTER_VERSION = 14`, marked DRAFT pending [USER] countersign. No
  measurement was run; no number was read for a decision.

## The central finding: the trail starts and ends at Track G

Searching *for* the document first required learning what the repo records
*about* it. The record is thin, and it is one-sided:

1. **2026-07-27** — Curtain Call's close-out mints the *question* as a "named
   follow-on" (`docs/curtain-call-sprint-log-2026-07-27.md:321`): the
   archetype-scorer / `RARITY_ODDS` question, out of scope under D12-frozen.
   It names a follow-on, **not** a registration document.
2. **2026-08-05** — Track G's roster-anchor report
   (`docs/roster-anchor-v14-2026-08-05.md` §4, commit `f77e14a`) writes, for
   the first time anywhere in history: *"The pre-registered payoff-reach /
   `RARITY_ODDS` sprint is a separate sprint with its own written
   predictions."* A `git log --all -S "pre-registered payoff-reach"` over
   every ref returns exactly this commit (plus Track X's later resolver
   commit `756647a`, which only re-indexes it). **No commit before f77e14a
   asserts a registration exists, and no commit anywhere contains one.**
3. **2026-08-05** — the sitting prep (§10.7) records that greps over `docs/`,
   `review/` and all branches had already failed, and the user-queue's §9
   fact-check row 3 states *"the document may not be in the repo."* This
   sweep confirms and extends that negative.

The most economical reading, stated as a finding and not a ruling: **the
registration was likely never a repo file** — Track G's author asserted it
from session context, and the "written predictions" lived (if anywhere) in a
conversation or an uncommitted buffer that no longer exists. Nothing found
contradicts this; nothing found confirms a file ever existed.

## Where we looked, precisely

### 1. Local worktrees FIRST (per [USER]'s note) — all 43, read-only

Enumerated `C:\Users\Monty\Documents\GitHub\GItS\.claude\worktrees\*`: 24
`agent-*` worktrees + 19 named ones (`land2`, `landCR`, `landEB2`, `landY`,
`landZ`, `s3-enemy-dossiers`, `s7-countersign`, `s7-fidelity`,
`s12-sentinel`, `track-b/e/f/g/g-d13/h/i/j/k/l/m/n/o`). For each: recorded
checked-out branch + HEAD, ran `status --porcelain`, and content-scanned
every untracked/modified file (and every file under untracked directories,
`game_ref`/`.git`/`__pycache__` excluded) for
`payoff[-_ ]reach | RA-G1 | RA-G2 | RARITY_ODDS | pre-regist`.

- **Dirty worktrees found:** `land2` (10 untracked Track O test fixtures —
  no marker hits beyond the already-committed
  `review/redteam/fixtures/track_o/s11_payoff_only_reach.py` family);
  `agent-aa0160f6124ddd499` (= Track P wave-8, in-flight edits to the queue/
  registries/DECISIONS + the Document-6 dispatch copy — expected, not the
  registration); `agent-a516b643cf8d865bb` (contains an untracked nested
  snapshot of the repo under `.claude\worktrees\s3-enemy-dossiers\` — every
  marker hit inside it is a byte-copy of an already-committed repo file);
  `landCR`/`landEB2`/`landY`/`landZ`/`s3-enemy-dossiers` and the primary
  checkout share one status whose only untracked entries are the worktree
  directories themselves and `.sentinel/` (inspected: `dll.json`,
  `relics.json` — not documents).
- **Registration-shaped files found: none.** No untracked or modified file in
  any worktree contains the markers outside byte-copies of committed files.

### 2. All branches, stash, and dangling objects

- **Branch tips (all 43 heads + remotes):** `git grep` of the marker set at
  every ref. The only files matching anywhere that do not also match at
  `origin/main` are the two wave-8 dispatch copies on
  `findings/track-p-wave8` (`docs/dispatch-2026-08-06-*.md`) — they cite the
  missing document; they are not it.
- **History:** `git log --all --diff-filter=A --name-only` — no file whose
  path contains `payoff`/`regist` was ever added and deleted other than the
  committed probe-registration drafts (`probe-d`, `probe-e`), which are
  different probes. `git log --all -S` for the pre-registration phrase: only
  `f77e14a` and `756647a` (above).
- **Stash:** `git stash list` — **empty** (one shared stash namespace for
  all worktrees).
- **Unreachable objects:** `git fsck --unreachable --no-reflogs` → 117
  commits, 247 trees, 43 blobs (full sweep, not sampled). Every unreachable
  commit was grepped for marker-bearing files not attributable to known
  committed paths: none. All 43 unreachable blobs were content-scanned: 2
  hits, both stale revisions of committed files
  (`docs/teyvat-spire-design-principles.md`,
  `docs/registry/identifiers.md`). Commit-message scan of all 117: every hit
  is a known sprint commit (fanfare/ghost-check/shop-channel lineage), none
  a registration.

### 3. Off-repo local locations (bounded, plausible)

- **Primary checkout root** (`C:\Users\Monty\Documents\GitHub\GItS`): only
  stray top-level file is the committed `README.md`; untracked entries are
  the worktrees and `.sentinel/` (inspected above).
- **Project memory** (`~\.claude\projects\...\memory\`): marker grep — two
  hits, both incidental (fanfare-sprint measurement recap, Klee rarity-walk
  note). No registration, and no memory file mentions one.
- **Session scratchpads** (`%TEMP%\claude\...`): marker grep across the whole
  tree — every hit is this session's own working files or the `mainbase`
  snapshot of committed docs. No prior session left a draft.

## Negative results, stated precisely

- No file named or shaped like a payoff-reach/`RARITY_ODDS` registration
  exists at any ref, in any working tree, in the stash, or among recoverable
  dangling objects of this repository.
- No commit message, ledger entry, docket row, or memory note names a
  **path** for the registration — nothing to restore *to*, because nothing
  ever said where it lived.
- The pinned drafter version the staged D15 change waits on (Document 6,
  item 10.3) is therefore **unrecoverable from the record**. The
  re-registration draft pins `DRAFTER_VERSION = 14` fresh; D15 lands only
  after the re-registered sprint runs under that pin (or [USER] re-sets it at
  countersign).

## Surfaced for the coordinator (no action taken here)

1. **`tto` columns:** the quarantine authority names the core-attainment
   columns; the `tto` columns in the same tables come from the same
   uncommitted throwaway harness (`RunResult.time_to_online`). Whether they
   ride the quarantine is a paper call not taken by this track (flag noted in
   the banner).
2. **Queue row 10.7 strike** and the D15 staged-pending row live in files
   Track P wave-8 currently has dirty (`docs/registry/user-queue.md`,
   `docs/dockets/engineering-backlog.md`) — left to Track P to avoid a
   collision; this report is the evidence the strike cites.
3. **Quarantine lift** is a paper act the coordinator handles with the wave,
   per the dispatch — the banner says so explicitly.

— Track S2, 2026-08-06. Files touched by this track:
`docs/roster-anchor-v14-2026-08-05.md` (banner only),
`docs/payoff-reach-reregistration-draft-2026-08-06.md` (new, DRAFT),
`docs/registration-hunt-report-2026-08-06.md` (this file).
