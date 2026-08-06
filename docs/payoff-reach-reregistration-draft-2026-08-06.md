# Payoff-reach / RARITY_ODDS sprint — clean re-registration (DRAFT)

> **Lifecycle: DRAFT — [USER] countersign REQUIRED before anything here
> operates.** A re-registration is a new probe registration, and probe
> countersigns stay with [USER] by standing pre-registration law (Class-P
> charter §2 explicitly excludes them). Nothing below is a prediction that has
> been graded, a number that has been read, or a measurement that has been run.
> **No measurement was run to produce this document.**

**Authority:** [USER], verbatim (2026-08-06, queue row 10.7): *"Let's yes to
both and see if it turns up on local."* — search-and-repair authorized; and:
*"If truly lost: re-register BEFORE any new number is read, never retro-fit a
registration to existing reads."*

**Search outcome this draft answers:** the original registration document was
**NOT FOUND** — not on any branch tip, not in any local worktree's working
files, not in the stash (empty), not among the object store's 117 unreachable
commits and 43 unreachable blobs, not in the primary checkout's untracked
files, not in session scratchpads or project memory. Full negative record:
`docs/registration-hunt-report-2026-08-06.md`. The hunt's central finding: the
**only** repo statement asserting that a pre-registration *exists* is Track
G's own scope fence (`docs/roster-anchor-v14-2026-08-05.md` §4, commit
`f77e14a`, 2026-08-05); no earlier commit anywhere in history writes the
words "pre-registered payoff-reach". The document may never have existed in
the repo at all.

**Consequence honoured here:** because the original cannot be produced, this
draft reconstructs the sprint's questions **only from what committed documents
say about it**, cites each source line, and pins the drafter version fresh. It
deliberately does NOT state predictions, thresholds, directions, or expected
values — the original's "written predictions" are lost, and inventing them now
would be exactly the retro-fit the authority forbids. Predictions are written
by [USER]-countersigned registration at kickoff, before any number is read.

---

## 1. What the repo says the sprint is (every citation)

1. **The question was minted as a named follow-on by Curtain Call**
   (`docs/curtain-call-sprint-log-2026-07-27.md`):
   - line 321–323: *"**Payoff-reach follow-on (from prediction 4):** the
     archetype-scorer / RARITY_ODDS question, explicitly out of scope under
     D12-frozen; this is the same named follow-on §9 already carried, now with
     a measured reason."*
   - line 277–283 (prediction 4's grade, the "measured reason"): *"under
     RARITY_ODDS, promoting payoffs OUT of common cuts their offer frequency,
     so rarity-shape correction REDUCED reach. Payoff reach must be bought at
     the drafter/odds layer or by in-rarity composition, not by promotion —
     named follow-on, and the D12-frozen discipline means nothing in this
     sprint could touch it."*
   - line 167–168: the mechanism's measurement context — *"HURT fanfare
     (payoff reach fell 2.12 → 1.26/deck: rarity promotion cuts offer
     frequency under RARITY_ODDS)"*.
2. **Track G asserts a pre-registration exists and fences itself off it**
   (`docs/roster-anchor-v14-2026-08-05.md` §4): *"`RARITY_ODDS` was not read
   for a decision and not touched. The pre-registered payoff-reach /
   `RARITY_ODDS` sprint is a separate sprint with its own written predictions;
   nothing above is graded against them, and no statement about how many
   payoffs an archetype should reach for, or about rarity, appears in this
   document."*
3. **The fence adjacency that forced 10.7**
   (`docs/sitting-prep-2026-08-05.md` §10.7): *"The re-baseline's
   core-attainment columns are measurement in the neighbourhood of 'payoff
   reach', and the payoff-reach/`RARITY_ODDS` sprint's registration document
   could not be located in the repo (greps over docs/, review/, all
   branches)."*
4. **A staged drafter change waits on the registration's pinned version**
   (wave-8 dispatch, Document 6, item 10.3, [USER] "Yes"): the
   spotlight-limb payoff-presence change is **DRAFTER 15**, staged-not-landed,
   because *"The payoff-reach sprint's pre-registration (whereabouts unknown;
   the 10.7 search is running) was registered against a specific drafter
   version. Until that document is found and its pinned version read, landing
   D15 could invalidate a blind pre-registration."*
5. **The instrument the sprint would read** (committed, unchanged):
   `tier05/exp_furina_ghostcheck.py` — *"PAYOFF REACH — how many of its OWN
   payoff cards the average fanfare deck actually contains"* (line 14), *"the
   payoff-reach count, which no other experiment [prints]"* (line 60). Prior
   published readings of that instrument (archive worlds):
   `docs/archive/furina-fanfare-sprint-log.md` (1.99 → 1.85 per deck across
   RT5→RT6, line 963; 1.87 under RT7, line 1057) and
   `docs/archive/ship-what-we-know-sprint-log.md` (1.87 → 2.03, line 610).
   Cited as the instrument's identity only — **no number here is being read
   for a decision.**
6. **The odds table itself**: `tier0/constants.py:800` —
   `RARITY_ODDS = {"common": 0.60, "uncommon": 0.35, "rare": 0.05}`.

## 2. The re-registered questions (reconstructed strictly from §1)

Q-A. *(from §1.1)* Can payoff reach be bought **at the drafter/odds layer**
     (archetype-scorer valuation and/or `RARITY_ODDS`-aware offer behaviour),
     rather than by rarity promotion — the remedy Curtain Call's prediction 4
     measured as counterproductive?

Q-B. *(from §1.1)* Can payoff reach be bought **by in-rarity composition**
     (payoffs living where the odds already put offers), the other arm the
     follow-on names?

Q-C. *(from §1.2)* What the original registered as "how many payoffs an
     archetype should reach for" — the target band itself. **Deliberately
     left blank here**: that is a design-shaped statement the lost document
     carried and this reconstruction may not invent. It is written at
     countersign or not at all.

## 3. Pin (fresh, at re-registration date 2026-08-06)

- **`DRAFTER_VERSION = 14`** (`tier0/constants.py:978`) — **the pin the
  staged D15 change waits on.** Per Document 6 item 10.3, the staged
  spotlight-limb change (`staged/d15-spotlight-payoff`) lands as DRAFTER 15
  only **after** this sprint runs under this pinned version (or the pin is
  explicitly re-set at countersign).
- Full world stamp at draft date: `RT7 / D14 / P3 / C5`
  (`RUNTEMPLATE_VERSION = 7`, `CONSTANTS_VERSION = 5`, `tier0/constants.py`).
- **Window caveat, surfaced not resolved:** the wave-8 dispatches open a v6
  window (`CONSTANTS_VERSION` 5 → 6: Frozen unified + α boss-room scope +
  shop-slot spec) with "no new quotable combat/shop number until the v6
  re-baseline sweep is green." Whether this sprint's window sits before or
  after v6 is a sequencing call for [USER]/the coordinator at countersign;
  this draft pins the drafter version and takes no position on the constants
  stamp.

## 4. What countersign must add before any number is read

1. The written predictions (direction + threshold per question), including
   Q-C's band or its explicit deletion.
2. Arms, n, seed, route, and cost ceiling.
3. Negative-control / anchor arms and the stop-and-re-register tripwire
   (house probe-registration shape, per the Q11 / probe (d) precedents).
4. The quarantine-lift linkage: on countersign, the `RA-G1`/`RA-G2`
   core-attainment quarantine (banner on
   `docs/roster-anchor-v14-2026-08-05.md`) becomes liftable per queue row
   10.7 — a paper act at the queue row.

**Countersign line (one word, [USER]): COUNTERSIGN / REVISE / DECLINE**

— drafted 2026-08-06, Track S2 (the 10.7 search), branch
`findings/track-s2-registration-hunt`. Zero design authority exercised.
