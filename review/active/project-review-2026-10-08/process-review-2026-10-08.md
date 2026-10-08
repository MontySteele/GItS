Status: OPEN (3 picks for [USER])

# Process workflow review, 2026-10-08

Written by Claude (Opus 5.5) as one part of the 2026-10-08 project review,
revised after a fact-check (log at the end). Numbers come from `origin/main`
at `e4255693`, `origin/klee-measure` (PR #929) and `origin/klee-next` at
`063e1b40`. Each count names the git or gh command it came from. Window:
2026-09-23 (the last process review) to 2026-10-08.

## Summary

The 2026-09-23 review's main cut held. No new R numbers. Seven paperwork
lints were retired. QUEUE went from 171 lines to 53. PRs land in minutes.

**The documents grew back, and the ruled Balance text is still not on
main.** STATE is 387 lines against the ruled "about 80", and BACKLOG doubled
from 70 to 147. Main's Balance paragraph cannot be followed as written: it
says to re-author rows onto the shipped sheets, and the legacy cleanup
deleted those sheets on 10-02. The text that replaces it was ruled on 10-05
but sits in PR #929, which now conflicts with main. Klee went through three
ruled card changes and a design review in 53 hours, each read off one
suite of five single runs. Three picks below. Everything else is hygiene.

## 1. What the 2026-09-23 review asked for, and where it stands

Source: `review/ruled/process-review-2026-09-23.md` sec. 4 and 5 (all four
picks at the defaults).

| Asked for | Now | Verdict |
|---|---|---|
| No new R numbers; the decision goes in the commit, in [USER]'s words | Held. 39 non-merge commit subjects since 09-23 say "ruled" (`git log origin/main --since=2026-09-23 --no-merges --format=%s \| grep -ci ruled`), and their bodies quote [USER] | Working |
| Retire the paperwork lints | `tools/lint_*.py`: 50 at `04840c5e`, 43 at `90b5eab8` (seven paperwork lints retired: experiments_active, packet_holds, r_numbers, register_ids, register_shape, review_status, rulings_index), 37 now. The second drop is the legacy cleanup deleting content lints (strict_domination, starter_pool_overlap and four more) plus two new lints (`git ls-tree --name-only <sha> tools/`) | Done |
| BACKLOG a short to-do list, one line each, deleted when built | 70 lines right after the trim (`90b5eab8`), 147 now. 25 bullets mention "seat page". 105 of 498 non-merge commits touched it (21%). The 09-23 review counted 509 of the last 1,000 commits (51%); counting all commits the same way now gives 125 of 865 (14%) | Grew back |
| STATE "about 80 lines" | 89 on 09-23, peak 445 on 10-05 (`6b42961c`), a partial trim the same day (`d5481498`, Furina's Stage history to its tag), 387 now (`git show <sha>:docs/current/STATE.md \| wc -l`). Not edited since 10-05 14:44 | Undone |
| QUEUE open picks only | 53 lines. Line 26 is stale (Klee's measurement plan "comes to [USER] as a paper"; ruled 10-05). Lines 27-31 are blank. #929, which is [USER]'s merge, is not listed | Mostly done |
| Seat rounds: two seats, a one-page record, transcripts gitignored | Transcripts are ignored. 64 new record files. Klee records run 51 to 266 lines (`klee-scaling-round-1` is 266). Balance suites are 5 seeds × 3 acts | Drifted (sec. 3) |
| Close old packets in `review/active` | 11 → 47 files. Only 6 files were added to `review/ruled` since 09-23, all from that day's batch. About 22 to 25 of the 47 carry a ruled, retired or superseded header (header scan, `git show origin/main:<file> \| head -25`). Both 08-13 packets the 09-23 review named are still there | Undone |
| Fix the skill contradictions about who merges | `open-pr` and `worktree` were fixed. `land-pr/SKILL.md` and `tools/land_pr.py:2,31` still say "PLUMBING only", a word CLAUDE.md no longer defines | Mostly done |

Where effort went: 200 of 498 non-merge commits (40%) touch no code and no
cards. Rule: a commit counts as code if any file is `.py`, `.cs`, under
`tools/`, `tier*`, `tests/` or `klee-mod/`; as cards if any file is a
`.yaml`. The 09-23 review reported 44% on its own sample. Most of that
paperwork now lands in STATE (76 non-merge commits) and in records.

## 2. Volume, rhythm and the PR flow

- **Throughput:** 498 non-merge commits in 15 days (`git rev-list
  --no-merges --count --since=2026-09-23 origin/main`). Most PRs merge
  within minutes of opening (`gh pr list --state all --json
  createdAt,mergedAt`). Two PRs are open: #929 (sec. 5) and #940, the
  standing klee-next staging PR marked "do not merge".
- **Merge safety:** two misses. #694 merged with red pytest (09-26). #943
  merged at 05:38:52Z and its first check started at 05:38:55Z (`gh pr view
  943 --json mergedAt,statusCheckRollup`). Main's CI passed afterwards.
  **The tool still has the #943 hole.** `tools/land_pr.py:153-162` only
  flags checks that are present and not green. With no checks yet, `bad` is
  empty and the verdict is GREEN. Hygiene, below.
- **Klee cycle time** varies a lot (`git log --all --since=2026-10-05
  --grep=klee --format='%h %ci %s'`):

| Step | Fastest case | Slower cases |
|---|---|---|
| Paper opened → ruled | design review 23:07 → 23:34 (10-07, a 630-line paper) | measurement paper 13:04 → 16:36 (10-05); defence paper 14:35, rewritten as tempo 19:52, ruled 20:21 (10-07, 5 h 46 min) |
| Record → its ruling | — | suite 2: 02:17 → 09:50 (10-07); scaling round 2: 10-06 01:00 → 10-07 01:37 |
| Ruled → built on klee-next | tempo 20:21 → 20:41 | — |
| Built → suite record | tempo build 20:41 → suite 4 record 21:47 | Boom Badge 09:54 → suite 3 record 14:24 |

  From 10-05 to 10-07 23:49 there were four suites, two scaling rounds and
  three ruled card changes to Klee: the scaling cards, Boom Badge to Common
  (a rarity change), and tempo (five cards out, five in). Then [USER] asked
  for a design review after suite 4 ("I think this calls for a design
  review", `klee-design-review-2026-10-08.md:6`). It was built on the tempo
  build, kept its cards, and changed two rules (growth 4 → 2, three opening
  Sparks) and two cards. Suite 5 is running now.
- **Ruled, then redone:** the clearest case is Furina. The re-founded Stage
  was frozen and its v2 discarded for the Salon's Tab (`43d5b7e6`). That is
  the Prototype stage doing its job: play overrules paper.

## 3. Are seat rounds the right size?

**At Prototype, yes.** Two seats find broken cards and a display that lies.
The Varka and Kokomi rounds have done that well.

**At Balance, a suite is about the right size, but one suite is a noisy
reading of one build.** A suite is one Sonnet run on each of five base
seeds, a fresh seat each act. A Klee-only suite costs "about 12M tokens"
(`klee-scaling-round-2-2026-10-06.md:163`). The ruled bar has three parts
(`origin/klee-measure:docs/current/operations/stage-gate.md:71`): the runs
reach act 3 as the base five's do; damage a turn and HP lost by act sit
within about 15% of theirs; and [USER]'s run says it is fun. The records
show how wide the noise is:

- Average end floor by suite: 30, 28, about 34, about 35
  (`klee-suite-2-2026-10-07.md:31`, `klee-suite-4-2026-10-08.md:21`).
  Suite 2's record calls its two-floor drop "seat-to-seat noise of that size
  is normal at one run a seed". Single seeds swing far more: the
  fact-check reads Necrobinder's seed at floor 33 in suite 3 and 9 in
  suite 4.
- Suite 3's act-3 HP-lost ratio is "9 fights from two runs". A 15% band is
  hard to read off 9 fights.
- The base-five baseline is itself five single runs, 0/5 at A0
  (`base-five-baseline-2026-10-05.md`). Every Klee ratio divides by it.

**The spend is not the problem. Reading each suite as a verdict on the
change just made is.** Suite 3 tested one change (Boom Badge to Common), so
it could be read that way. Suite 4 tested ten card changes at once. It can
say "act 2 got better"; it cannot say which change did it. The design review
did not rest on suite-to-suite noise: its finding is a turn-one gap of about
50 points (Klee 5 to 9 damage against 57 to 62, `klee-design-review:44-46`).
Pick 2 is about the smaller calls.

**Co-op check:** the paired reaction round (`coop-reaction-round-2026-10-07.md`)
says itself: "One run a side is routing noise." Its first attempt was
abandoned on a desync at floor 24 (#948), and the rerun stalled at the
Crystal Sphere (#949). The 10-06 ruling already says the co-op check is "a
paired seat round on shared seeds", plural (`stage-gate.md:85` on main), so
one seed fell short of the rule. Running it as written is hygiene. Pick 3
covers only how often.

## 4. How often did a seat verdict mislead?

Nine cases in 15 days, checked against the quoted records. By cause:

| Cause | Cases | Fix in place? |
|---|---|---|
| **The instrument was wrong** | Base controls ran on cut pools until #924 (10-05); the incoming-damage line was wrong in four ways (#925, #926) | Yes. Control comparisons before 10-05 are suspect |
| **Seed luck read as a trait** | "Klee strong in act 1" was "partly luck of the seeds" (suite 1); the co-op round was one run a side | No. Picks 2 and 3 |
| **The test could not see the change** | Scaling round 2 missed its gate as written ("The gate (written before the round)", `klee-scaling-round-2-2026-10-06.md:49`); suite 2 then "re-measured suite 1" because the new cards reached decks late, and ran "despite round 2's missed gate" (`klee-suite-2-2026-10-07.md:3`) | Partly. The gate written in advance caught it |
| **A prediction missed while the result moved** | Suite 4: the paper's own measures "all missed, while the result improved" (`klee-suite-4-2026-10-08.md:52`) | Reported honestly |
| **A seat's taste read as a cut** | Kitchen Alchemy "NEVER AGAIN", then [USER] kept it: "it's quite good!" | Yes (memory `seat-verdicts-not-cut-lists.md`) |
| **Seat skill** | Sonnet seats "race damage instead of blocking"; base five 0/5 at A0, while [USER] wins through A5 | Handled by the relative bar |

**Reading:** only one case was a seat's opinion misleading. The rest came
from the instrument or the sample size. [USER]'s own run stays the clearest
verdict, and it is already scheduled: design review pick 5 (ruled 10-08)
puts his run on the build that passes suite 5, with his turn-one plays
noted.

One precedent is worth knowing. The Prototype finish line is "fun through
act 3" in [USER]'s run (`stage-gate.md:55-56` on #929's branch). STATE says
Klee's "finish line was met without a further run on this build"
(`STATE.md:100`). [USER] made that call, and it was his to make. It does
show that a stage label can move ahead of the play it names.

## 5. Is the Balance-stage measurement law pulling its weight?

**The law as written on main: it has not been used for a kit at Balance,
and it cannot be.** `EXPERIMENTS.md` was used in August for registered,
blind-graded runs (`KLEESPARK-R2`, 2026-08-29, line 301, and the rows near
it). It has had no commits since 09-23. Main's `stage-gate.md:71-72` says
Balance means re-authoring accepted rows "onto the character's real sheet",
then pre-registration and "the twelve-arm re-baseline where one is owed"
(lines 74-75). The real sheets were deleted by legacy cleanup stage 6a
(`ad369ea1`, 10-02). STATE also contradicts itself: line 45 says Klee is at
Balance, line 373 says `EXPERIMENTS.md` is dormant.

**The law as ruled on 10-05 is working in its light form:** the real-game
bar, a build freeze with `klee-next` staging, and a one-line prediction per
change graded by the next suite. The freeze works: main's Klee has not
moved, and klee-next is 6 non-merge commits ahead of main (`git rev-list
--no-merges --count origin/main..origin/klee-next`) and 8 behind.
**But that text exists only on `origin/klee-measure`, PR #929**, ruled on
10-05 ("looks good to me!", `0fefc6be`). It now conflicts with main in
`stage-gate.md`, where main added the "Solo first, co-op checked" paragraph
on 10-06 (`3ef53dc9`), and three of its CI jobs were cancelled (`gh pr view
929`: CONFLICTING; pytest 1/4, pytest 4/4, lints, patch-sentinel
CANCELLED). It amends `EXPERIMENTS.md`, so it is [USER]'s merge. Pick 1.

**Where does a frozen kit's state live?** STATE on main still says Klee's
"measurement plan being drafted" (line 45) and records none of suites 1 to
4, the scaling, tempo and design-review rulings, or the growth and Spark
rule changes. Under the freeze those live only on klee-next and in records.
Hygiene: a short "staging" line in STATE's Klee entry naming the branch,
the build and the latest record, updated as each suite lands.

**Stale guidance a Balance session can still hit:** the `sitting` skill
(`.claude/skills/sitting/SKILL.md`, last changed 09-23) still says "Use for
any pre-registered cell" and walks through countersigns, R212, tripwire S1
and "update the registers". The ruled 10-05 text says slates and
countersigns do not gate kit balance (`0fefc6be` body). Hygiene.

## 6. Is design work landing in the right model?

**This cannot be checked from git.** Commit trailers do not tell the main
session from a subagent. The papers read look main-session-authored, and
their GPT and Fable reviews were relayed and folded in as allowed (for
example `78d66153` and `dd5090fb` on the scaling paper). **One live risk is
tonight's fan-out:** subagents are writing review papers with design
judgements in them. Those should reach [USER] as input to a main-session
synthesis, not be ruled directly.

## 7. What is left undone

1. **STATE back to about 80 lines.** It grows because each round appends a
   paragraph. The kits section runs from line 58 to 357: Klee 50 lines
   (58-107), Kokomi 116 (108-223), Varka about 92 (226-317), then relic and
   element-port notes. Retired prose goes to git, cited by commit or tag, as
   `d5481498` already did for Furina.
2. **BACKLOG back to one line per item.** 147 lines; the 25 seat-page lines
   are the biggest cluster.
3. **`review/active` back to live papers only.**
4. **Records back to one page.** A suite record should be a fixed table:
   ratios, end floors, the prediction line graded. Analysis goes in the
   paper that uses it.
5. **Papers [USER] rules: about two pages.** The design review is 630 lines.
   The norm exists; enforce it with a two-page top and an appendix.
6. **The main checkout is stale.** It is 33 commits behind `origin/main`,
   with 62 untracked `understudy/logs/*.log` files and a modified tracked log
   (`git status --porcelain`). The logs are not gitignored (`git
   check-ignore` exits 1). CLAUDE.md tells a fresh session to read STATE from
   that checkout, so it reads old docs, and the untracked logs feed
   `land_pr`'s untracked-file trap. Wait for the Klee suite to finish before
   touching it.

## Hygiene Claude can just do

- `tools/land_pr.py`: an empty or still-pending check list REFUSES ("no
  checks reported"), with a test. Closes the #943 hole.
- Change "plumbing" to "a PR that asks nothing of [USER]" in
  `.claude/skills/land-pr/SKILL.md` and the `tools/land_pr.py` docstrings.
- Rewrite STATE to about 80 lines (sec. 7.1). Fix line 373 against line 45.
  Add Klee's staging line (sec. 5). Retire the "Live cell" stamp list.
- QUEUE: delete the blank lines 27-31 and list #929 as [USER]'s merge.
  (Line 26 and STATE line 45 are already fixed inside #929; do not duplicate
  them.)
- `review/active`: move every ruled, retired or superseded paper to
  `review/ruled/`, including both 08-13 packets
  (`eb74-lever2-options-2026-08-13`, still OPEN; `p2-hard-state-thresholds-2026-08-13`,
  RETIRED). Correct the stale headers: `klee-overhaul-round-26-2026-09-08`,
  `klee-overhaul-slice-1-2026-09-01`, `kokomi-overhaul-slice-1-2026-09-01`,
  `furina-stage-round-1-2026-09-08`, `furina-stage-brief-2026-09-08` (frozen
  build), `furina-v2-review-packet-2026-10-05` ("FOR REVIEW", but v2 was
  discarded), `klee-turn-one-paper-2026-10-08` (superseded by the design
  review), `kokomi-core-pass-2026-09-27` ("BUILDING"). Keep `klee-brief` and
  `kokomi-brief` OPEN; they are the live briefs. Check `companion-cards`,
  `furina-design-layer` and `reaction-brief` against STATE before moving.
- BACKLOG: merge the 25 seat-page lines into one grouped section and strip
  dates and round citations from the bullets.
- Add a suite-record template to `operations/understudy-seats.md`: one
  table, the prediction line graded, the picks. About 50 lines.
- The `sitting` skill: say at the top that it applies to sim-law
  registrations only, not to kit balance, and drop the R-era steps.
- Run co-op checks as the 10-06 rule says: shared seeds, plural.
- Once #929 lands: one line in CLAUDE.md's seat norm, "a Balance suite is
  five base seeds × three acts".
- The main session writes the fan-out synthesis. Subagent papers go to
  [USER] as attachments.

## Picks

**Pick 1: land PR #929 (the ruled Balance text).** Main's Balance paragraph
cannot be followed: it re-authors onto sheets that were deleted on 10-02.
#929 conflicts with main and has cancelled CI jobs, so it cannot merge as
is.
1. **Default:** Claude rebases #929 onto main, keeping main's 10-06 "Solo
   first, co-op checked" paragraph, and adds a pointer at the top of
   `EXPERIMENTS.md` that its sim-law half does not gate kit balance. CI
   reruns; [USER] merges.
2. Rebase only, with no `EXPERIMENTS.md` pointer; [USER] merges.
3. Leave it open.

**Pick 2: when a Balance direction may be replaced.** #929 already rules
that each change carries a one-line prediction graded by the next suite.
What is new here is a replication rule for smaller calls.
1. **Default:** each suite tests one named change set. A change is reverted
   or replaced on a suite result only if a second suite on the same build
   agrees, unless the gap is plainly outside the suite-to-suite spread seen
   so far (end floors moved 2 to 6 between suites). Large structural
   findings, such as the design review's turn-one gap, are not held to
   this. Cost: about 12M tokens per replication.
2. As now: one suite per change. Fastest; a call can flip on noise.
3. Two seats per seed per suite (about 24M a suite). Better ratios, same
   cadence.

**Pick 3: how often the co-op check runs.** The 10-06 rule fixes its shape:
a paired seat round on shared seeds, kit pair against Ironclad + Silent.
1. **Default:** three shared seeds, run once at a kit's finish line and
   after any reaction-rule change. No co-op round between card batches.
2. After every card batch as well.

Where the evidence is thin: every Klee ratio rests on five single runs a
suite, and the base bar on five single runs. Suite 3's act-3 ratio rests on
9 fights. The co-op comparison rests on one run a side. Model routing
cannot be audited from git.

## Fact-check log

Accepted and fixed:
- Old pick 4 (Klee's next step) dropped. Design review pick 5 (ruled 10-08)
  and #929's bar already schedule [USER]'s run; sec. 4 now says so.
- Pick 1's default is now the rebase. Confirmed: `gh pr view 929` shows
  CONFLICTING and three cancelled jobs. QUEUE line 26 and STATE line 45 are
  already fixed inside #929 (`git diff origin/main...origin/klee-measure`),
  so those hygiene items were removed.
- Sec. 3 states all three parts of the ruled bar, including [USER]'s run.
- "Never used" became "not used for a kit at Balance, and cannot be". Added
  that the shipped sheets were deleted (`ad369ea1`).
- Added "where one is owed" to the re-baseline quote.
- Commit counts are now non-merge: STATE 76; BACKLOG 105 of 498 (the
  fact-check said 107; main has moved to `e4255693` since). The 09-23
  comparison is shown both ways.
- Lints split: seven paperwork lints retired (50 → 43); 43 → 37 is the
  legacy cleanup plus two new lints. Verified by `ls-tree` diff.
- `review/active`: 8 ruled papers became "about 22 to 25"; only 6 files
  added to `review/ruled`; both 08-13 packets named.
- Stale-header list extended (`furina-v2-review-packet`, `klee-turn-one`,
  `p2-hard-state`); live briefs kept OPEN.
- Prediction catches reattributed: the missed gate was scaling round 2's;
  suite 2's record has no prediction line (grep finds 0).
- "Ruled then reversed, 8 cases" removed. The Bomb relic, Kitchen Alchemy
  and the Jean revert were not reversed rulings.
- Klee "four directions" softened: Boom Badge is a rarity change, and the
  design review was [USER]'s request, built on tempo, resting on a large
  turn-one gap.
- Pick 2's "2 floors / 0.2 ratio" threshold removed; the observed 2-to-6
  floor spread is quoted instead, and the pick notes what #929 already
  rules.
- Pick 3 cites the 10-06 rule; running it as written moved to hygiene;
  option 3 and the "telemetry from [USER]'s runs" default removed.
- The `EXPERIMENTS.md` pointer moved from hygiene into pick 1.
- History goes to git, not the brief. Klee's entry is 50 lines; Kokomi's
  116 is named as the bigger problem.
- Cycle-time table now shows the slow cases next to the fast ones.
- Minor: records 51 to 266 lines; klee-next 6 non-merge ahead (8 behind at
  `e4255693`); the co-op run was abandoned, not lost.
- Scratchpad sources replaced with the git or gh command, or the counting
  rule written out.
- Gaps added, each checked: BACKLOG 70 → 147; STATE not edited since 10-05
  and no home for frozen-kit state; the stale main checkout and untracked
  logs; the `sitting` skill; the finish-line precedent (`STATE.md:100`);
  QUEUE blank lines and #929 missing from it; open PR #940; STATE's 10-05
  peak and partial trim.

Rejected or adjusted:
- Varka's STATE entry is about 92 lines (226-317), not about 130. Lines
  318-357 are relic and element-port notes, not Varka's.
- STATE's peak was 445 lines (`6b42961c`, 10-05), not 441.
- "[USER]'s 10-01 run died mid act 2" was not checked and is left out. The
  precedent is cited from `STATE.md:100` alone.
- The fact-check's per-suite act-3 fight counts (8, 9, 18) were not
  reproduced; the telemetry feed mixes sources. The paper quotes only suite
  3's own "9 fights from two runs".
- Untracked logs: 62 now, not 63.
