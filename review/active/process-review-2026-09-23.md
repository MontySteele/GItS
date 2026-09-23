Status: OPEN (four picks, §5)

# Process review: keep the safety rails, drop the paperwork

Written 2026-09-23 by Claude (Opus 5.5) at your request, from a measured
census of the repo at `04840c5e`. Every number below was counted from the
repo. The raw census is not committed. One sentence up front: the
machinery that keeps the game from breaking is cheap and worth keeping; the
machinery that keeps the paperwork consistent with itself is expensive and
mostly not.

## 1. Where the effort went

- **Half of all recent commits edit the backlog.** 509 of the last 1,000
  commits touch `BACKLOG.md`. 44% of those 1,000 touch no code and no card
  at all, and only 21% touch no process file.
- **One ruling costs two commits, a PR, and a code edit.** Recording R271 or
  R275 meant the ruling commit, a separate "RULINGS index" regeneration
  commit, a PR merge, and a hand edit to a number inside
  `tools/lint_r_numbers.py`. Closing a backlog row means editing a hand-kept
  list inside `tools/lint_register_ids.py` (44 of the last 1,000 commits).
- **About 5,300 lines of Python exist only to keep registers, rulings, ids,
  stamps and packets consistent with each other.** That is ten lints plus
  the ruling-index, row-minting and PR tools.
- **The largest instruction file is an id ledger.**
  `operations/register-ids.md` is 1,744 lines, and 1,619 of them are
  notes on which backlog numbers were minted and retired.
- **Seat rounds produced over half a million lines.** `review/qa` holds
  528k lines of raw seat transcript, from about 73 rounds that almost all
  ran in one week (2026-09-02 to 09-09). Kokomi alone had eight rounds on
  2026-09-08.
- **275 rulings in 60 days**, about 4.6 a day. That pace is more than a person can
  read. It is what "one packet per decision" produces when decisions are cut
  small.

## 2. What is working and stays

- **The four safety hooks** (no `git add -A`, no push to main, no deploy
  from a worktree, no skipped pre-push gate). They fire on every shell
  call, cost nothing noticeable, and each one exists because something was
  lost once.
- **The pre-push gate and CI.** 7,938 tests run in about a minute, and the
  38 CI lints run in under three seconds. The ~42 lints that check code and
  content (C#/Python parity, codegen, art coverage, text encoding) are the
  real backstop.
- **The Paper → Prototype → Balance idea**, and the rule that measurement
  law binds only at Balance. Nothing is at Balance today, so most of
  `EXPERIMENTS.md` is simply dormant, which is correct.
- **The character brief as the design record.** Klee's and Furina's briefs
  are good documents. They are what a new session should read.
- **You play when a rule changes.** Both Klee runs gave the clearest
  verdicts in the record.

## 3. What is not working

1. **Ids and rulings for everything.** R numbers, EB numbers, M numbers, D
   numbers, stamps, slices and "pick 5.1" section ids all live in parallel,
   and lints check that they agree. A decision you make in one sentence
   currently turns into 3 to 11 file edits. Git already records who decided
   what and when.
2. **The backlog is a diary, not a to-do list.** Its header says "only open
   work", yet 42 of its 73 rows say BUILT. Rows are rewritten on every step,
   which is why half the commits touch it.
3. **Seat rounds became the unit of progress.** A round should answer a
   question the design has. Too often a round produced six new text-defect
   rows and one read, and the next round was scheduled to read those.
   Klee had 27 rounds on a kit you had already called sound twice.
4. **Packets are written for the lints as well as for you.** Round reads
   carry build hashes, stamp disclosures, D/E/F defaults and register
   cross-references. You do not need most of that, and it is where the
   Fable usage went.
5. **The rules contradict themselves in small ways.** The worktree skill and
   a hook's docstring still say PR merges are yours, which R259 reversed.
   QUEUE's header still says it mints ids, which ended 2026-09-01. STATE is
   238 lines against "near 150", and its heading is dated 09-08. CI lists 27
   lints by hand while `run_lints` has 38. Two review packets from 08-13 sit
   in `review/active`, and one packet is 1,071 lines against the
   1,000-line rule.
6. **PR #476 has been open since 2026-09-09** with a Furina pick in it. It
   reuses backlog ids EB-749 to EB-754, which main has since given to Klee
   rows. The id machinery did not prevent the collision it exists to
   prevent.

## 4. The proposal

**Decisions.** Your decision goes in the commit message, in your words, and
the brief it changes is edited in place. No new R numbers. `RULINGS.md` is
frozen as history, and the R-number and rulings-index lints retire. A pick
still comes to you as a numbered list with a default. It is named by the
document and number ("Klee review, pick 2"), which is enough to find it in
git.

**Backlog.** `BACKLOG.md` becomes a short open to-do list, one line per item
with no required fields. A built item is deleted in the commit that builds
it. EB ids stay on existing rows so old citations still resolve, but the
ledger in `register-ids.md` and the `RETIRED` list in the lint go. The
register-shape and register-ids lints retire, and so do the packet-holds,
review-status and experiments-active lints, which police the same
paperwork.

**Seat rounds.** Run one when a rule changes or a batch of new cards lands,
and not otherwise. Two seats by default. The raw transcripts stay on disk
and are gitignored. The committed record is one page with three parts: what
played well, what did not, and what to change. Display defects go into the
to-do list as one line each. They don't get their own paragraphs.

**Documents.** One living brief per character, plus the card sheet. Round
packets are notes against the brief, not new authorities. STATE is
rewritten to about 80 lines and says only what ships and what is next.
`workstreams.md` (1,203 lines) and `register-ids.md` are frozen, not
maintained. `understudy-seats.md` (1,271 lines) is cut to the procedure a
seat actually needs. The contradictions in §3.5 are fixed in the same pass.

**The delegation ladder** reduces to one sentence: Claude decides and ships
everything except a design direction, eyes-on taste, money, and
one-way doors, which come to you as numbered picks.

**What does not change:** the hooks, the pre-push gate, CI, the code and
content lints, the Balance-stage measurement law for when a kit gets there,
and "starter cards stay bad."

**The cost of doing it:** one Claude sitting, mostly deletions. Nothing is
lost, because git keeps every retired file under a tag, as the 08-06
simplification already does.

## 5. Picks

**Pick 1: decisions without R numbers.**
1. **(default)** No new R numbers. Your words go in the commit message, the
   brief is edited in place, and `RULINGS.md` is frozen with its two lints
   retired.
2. Keep R numbers, but generate the ceiling and the index from git so no
   lint needs a hand edit.
3. Keep as is.

**Pick 2: the backlog as a to-do list.**
1. **(default)** Open items only, one line each, deleted when built. Stop
   maintaining the id ledger, and retire the five paperwork lints named in
   §4.
2. The same, but move the to-do list to GitHub issues.
3. Keep as is.

**Pick 3: seat rounds.**
1. **(default)** Only on a rule change or a new card batch. Two seats, a
   one-page record, and transcripts gitignored.
2. The same, and also stop committing the existing `review/qa` history,
   deleting it from HEAD under a tag.
3. Keep as is.

**Pick 4: the trim pass.**
1. **(default)** Claude runs the whole trim in one sitting as one PR: STATE
   rewritten, the delegation ladder in one sentence, the contradictions
   fixed, and the frozen files marked. You read the PR and veto.
2. Do picks 1 to 3 only, and leave the documents alone for now.
