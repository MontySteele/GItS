# The machinery review — how a character moves from an idea to the table, and where the fun goes

**Written 2026-09-01 on branch `kit-overhaul-2026-09-01`. Paper only.** Nothing
here changes LAW, a register, a stamp, or a process. It is an assessment with
numbers behind it, and a numbered list of changes at the end, each with a
default you can veto.

Three read-only audits were run for this document and their facts are cited
inline: a trace of one mechanic change end to end (the Klee Sparks redesign,
2026-08-29 to 08-31), an audit of every pick put to you between 08-28 and
08-31, and a summary of what the measurement law and the blind seat require
and can see. Where a number is theirs I say so.

---

## 0. The short version

- **The machinery is good at what it was built for.** Defects, parity between
  the two engines, honest measurement, independence between author and
  grader, and throughput. An idea became a sealed blind run inside a day, more
  than once.
- **It was built to measure balance and catch defects. It was never built to
  find fun, and every instrument in it says so in its own text.** The seat is
  told "you are not being asked whether this is fun." Guardrail-7 reserves fun
  to you alone. And the standing rule (R217 A) says you play no forms and no
  turns during iteration. So the only fun instrument in the building is, by
  rule, switched off while the design is being iterated. That is the doom
  loop, stated exactly.
- **One change costs a lot and moves nothing shipped.** The Sparks redesign:
  34 branches, 35 PRs, 12 rulings, 28 backlog ids, 208 tests, 8,068 lines of
  prose, 200-plus Codex calls, and at the end zero shipped Klee card rows
  changed. Its governing pick and its eyes-on gate were still open when the
  window closed.
- **More than half of what came back to you did not need you.** 145 picks in
  four days; 56% were defaults the ladder already determined, names and
  constants, or questions the process created about itself. You answered 94%
  of all picks at the packet's own recommendation. You also merged 111 PRs in
  those four days, 43 of them touching no code, sheet, or asset.
- **The picks that mattered were the ones with no default,** where you wrote
  your own words: the Burst retirement, the stage rules, Prune's re-author,
  Furina's sixth slot. The pick-list form is optimised for the other kind.

The fix is not less process. It is process that asks for the right evidence
at each stage: taste first, on paper; play second, on a build; measurement
last, on a sheet. Today all three are asked for at once, and the one that is
cheapest to ask for early is asked for last.

## 1. What the machinery is

One paragraph, so we agree on the map. A design idea is written into a packet
in `review/active/` with numbered picks. A doctrine seat (GPT) reads it
against the D1 to D9 charter. Claude drafts a prediction slate and commits it
before any run. The mechanic is built in the Python sim behind a flag, then
in C# behind the same flag, on the quarantined prototype surface. A dev build
is deployed with a `+proto` mark and soaked for three fights. Staged turns are
boarded, read blind by a grader who sees only card faces and intents, graded
on a four-question form, and replayed live. A pair read returns ADVANCE or
RETURN. ADVANCE earns a sealed whole-fight run and a second pair read. The
results, picks and countersigns are assembled into one slate per sitting and
ruled under one R-number. Accepted rows are re-authored onto the real sheet
under a `CONSTANTS_VERSION` bump, the sheet digest is re-pinned, and a twelve-
arm re-baseline may be owed. Every step leaves a register row, a packet
section, and often a branch and a PR that you merge.

## 2. What it is good at

Say this first, because the changes below keep most of it.

- **Defects.** Forty-nine lints, 4,451 tests, a soak on every dev deploy, a
  bite-check that patches the game assembly outside Godot. Structurally
  invisible defects became curated lists with lints. This works and nothing
  below touches it.
- **Honest numbers.** Stamped worlds, one-variable windows where attribution
  matters, prediction slates committed before runs, blind grading, records
  that are struck rather than rewritten. The re-baseline itself is cheap: 12
  arms, 3,000 runs each, 152 seconds.
- **Independence.** Two model families, authorship recorded per row, a seat
  that refuses to grade its own family's work. This caught the Klee grading
  breach and it will catch the next one.
- **Throughput.** Kurage Memory went from your paragraph to a sealed blind run
  in one day. The Sparks redesign ran twelve registered cells in thirty-four
  hours. The pipeline moves.
- **The delegation ladder (R212).** It is the right instinct and it is
  already saving picks. It stopped short.

## 3. The doom loop, with the evidence

The instrument summary is unambiguous, and I quote it because it is the
crux: *"Nothing in this machinery can detect that a kit is unfun, and every
instrument says so in its own text."*

- The grader prompt: "You are not being asked whether this is fun. Any
  judgement of quality is outside what you were given and outside what is
  wanted."
- Guardrail-7, second rule: "No fun, ever. Legibility, readability, feel and
  fun remain [USER]-only instruments and nothing in this directory may be read
  as evidence about them."
- R217 A: [USER] "plays no forms and no calibration turns during iteration,"
  and the down-weighting that depended on it is marked dormant.

So: the seats can say a turn had two lines and the enemy's intent mattered.
They cannot say the two lines were interesting. Closeness is "best line less
than twice the runner-up," which a choice between three flavours of damage
passes easily. ADVANCE means "worth asking again with whole-fight play," and
it is written on every verdict that it is not approval, but it is the only
positive signal the loop produces, so it functions as one. Six ADVANCEs on
the Kokomi slice and you found the kit one-note. The same thing happened on
2026-08-26 after the richness pass. The loop ran twice and converged on the
same place because it was optimising for the thing it could measure.

What each instrument *can* see, so it is used for that and not more: the
form sees decision-presence; closeness sees one-line dominance; the sim sees
relative deltas and structural findings; blind play sees completability and
face leaks; scenarios and soak see defects. All of those are worth keeping.
None is a fun gate.

## 4. The cost of one change

From the trace of the Sparks redesign, 2026-08-29 03:29 to 2026-08-31.

| What | Count |
|---|---|
| Branches touching the arm | 34 |
| PRs merged for it | 35, about 37% of all merge traffic in the window |
| Rulings | 12 |
| Backlog and pick ids minted | 28 EB, 5 M; 7 EB still open |
| Registered cells / runs / staged boards / sealed sessions | 11 / 12 / 26 / 5 |
| Codex calls | at least 201 |
| Tests added | 208 in 16 files |
| Prose written | 8,068 lines; the packet grew 571 to 7,514 lines in 34 hours |
| Decisions put to you | 53; 34 answered, 19 open at the end |
| Shipped Klee card rows changed | 0 |
| Prototype rows minted | 12, plus one companion re-author |

Two things in the trace deserve their own line. First, the runs `W1`, `W2`,
`S1`, `W3`, `BT1`, `BT2` and `BT2r` are each written as "offered for batch
countersign" and each ran, but no ruling id records the countersign. Seven
runs rest on an implied signature, which is the pre-registration rule
quietly not holding. Second, the arm's own governing pick, the six-option
sink set in §20.5, was never answered and no register row was minted for it.
The process produced everything except the decision.

The stages that changed the design, per the trace: your intent paragraph;
the Regent research (income already matched, the gap was sinks); the first
staged round (the arm was "legible as a shape, inert as a decision"); and
the BT2 rerun that fired a return condition. Four stages out of roughly
fourteen produced information. The rest produced records.

## 5. What came back to you, and what did not need to

From the audit of 145 picks between 2026-08-28 and 08-31.

| Class | Count | Share |
|---|---|---|
| A. A design fork a brief could not settle | 40 | 28% |
| B. Taste, eyes-on | 11 | 8% |
| C. Money, one-way door, LAW amendment | 13 | 9% |
| D. A default the ladder or a ruling already determined | 53 | 37% |
| E. A name, wording, constant, upgrade delta, or id | 15 | 10% |
| F. A question the process created about itself | 13 | 9% |

D plus E plus F is 81 of 145. Of those 81, you answered 80 at the packet's
own recommendation. Across all 145, 94% landed on the recommendation. Nine
picks came with no default at all, and those nine include four of the most
consequential design answers of the period. The pattern is plain: **when the
packet had a default, you took it; when it had none, you designed.**

Ten questions were asked more than once in different words, including the
Bag of Tricks price (four times), the Klee sink set (three), and the memory
cap (three, once returning UNREACHED). One pick was ruled twice inside the
same slate. One id, "PICK 3," names two different things inside the same
packet.

Merges: 111 by you in four days. Five touched only registers, indexes and
logs. Forty-three touched no code, sheet, or asset. Sixty-eight carried
content.

## 6. Where the process kills fun, specifically

These are mechanisms, not blame. Each one is a reasonable rule that has a
side effect on design.

1. **Taste is asked for last.** To feel a mechanic you need the sim, the C#,
   the bridge, the UI, a deploy, and a sealed run. By then twenty branches
   exist and the question "is this fun" arrives with a sunk cost attached.
   The paper stage, the cheapest place to ask, has no gate at all: no D1
   brief was ever written for Klee or Kokomi, and the charter that asks for
   one was ratified after both kits shipped.
2. **The pick list turns design into multiple choice.** A packet drafts
   options A to D and a recommendation. You pick. The audit shows you almost
   always pick the recommendation, which means the design is effectively
   Claude's, filtered through a yes. The four best decisions of the period
   were the ones where no options were offered and you wrote a paragraph.
   The form suppresses exactly the input the project is missing.
3. **Identity is a statline in LAW.** "Character identity = statline
   asymmetry," Klee's scaling cap, Kokomi's no-healing-ever and one-
   destination Charge. A statline produces "more damage, less block" by
   construction. Changing it is a LAW amendment, which is ceremonially
   yours, so nobody proposes it, so the kit is designed inside the box.
4. **The seat's positive signal is a negative test.** SURVIVES means "not yet
   falsified"; ADVANCE means "ask again." Both are correct and both read as
   green. A loop with only a red light and a "not red yet" light will drift
   toward whatever is not red.
5. **Prose replaces reading.** `review/active/` is 42,588 lines. One packet is
   7,514. You cannot read it, so you rule on a summary; the next agent cannot
   read it either, so it re-derives, re-asks, and writes more. Ten re-asks in
   four days is what that looks like.
6. **Measurement law is applied to exploration.** Stamps, windows,
   pre-registration and countersign exist so that a published number means
   something. Applied to a prototype nobody will ship, they add a slate, a
   countersign, a ruling, and a record to a question whose only honest answer
   is "play it and see." The trace shows the countersigns going implied under
   that load.

## 7. What I would change

Ten changes. Each names what it replaces and carries a default. You veto on
sight.

1. **Three stages, three kinds of evidence.** *Paper* is gated by your taste:
   a brief and turn scripts, read in fifteen minutes. *Prototype* is gated by
   play: a flag, a build, two fights by you, one sentence back. *Balance* is
   gated by measurement: sheet, stamp, re-baseline, bands. Measurement law
   binds only the third. The prototype stage gets no slate, no countersign,
   no register row, no re-baseline. **Replaces** the current single path where
   all three are asked for together. This is the change; the rest are
   consequences.
2. **Restore the human fun gate, and keep it cheap.** The calibration forms
   failed because they asked you to grade turns. The fun gate asks you to
   play two fights on a `+proto` build and answer one question, chosen in the
   brief before the build exists (for Klee: "did you ever choose to cook?").
   Seats keep legibility, defects and independence. Nothing else can see fun
   and the machinery says so. **Replaces** R217 A's blanket "no turns during
   iteration," which was aimed at forms, not play.
3. **Default-and-veto everywhere.** Classes D, E and F are applied by Claude
   and disclosed in the slate as APPLIED, with the five-day veto R212 already
   has. Only A, B and C return, and every one of those carries a default.
   Where a genuine design fork has no default, it is put as an open question
   with a blank paragraph, on purpose, because that is where your best
   answers came from. **Replaces** the pick-list-for-everything rule, and
   would have removed 81 of 145 picks.
4. **A ruled pick is closed by id.** A re-ask must cite the new fact that
   reopens it, in one line, or it is not asked. **Replaces** nothing written;
   it stops the ten re-asks.
5. **Prose diet, with numbers.** A decision memo you must read is two pages;
   the argument is an appendix. STATE.md at 959 lines is not an always-read
   document; it becomes 150 lines of pointers. A ruled packet leaves
   `review/active/` for a `review/ruled/` directory the same day, so the
   active set is what is actually active. The 7,514-line packet pattern is
   retired: a packet that grows past 1,000 lines is split by decision, not
   extended. **Replaces** the current habit, not a rule.
6. **Split LAW.** Engineering invariants, measurement law and the shared
   combat rules stay LAW and stay ceremonial. Character-identity statements
   (the statline pillar, per-character resource laws, the healing law as it
   applies to one character) move into that character's brief, owned by you,
   revised at a sitting by a sentence, with no amendment ceremony. The D1 to
   D9 charter becomes the review checklist a brief is read against, not a
   gate rows pass. **Replaces** the current placement, and is itself a LAW
   amendment, so it is yours.
7. **Prototype in the engine people play.** For the prototype stage, build
   the flag in C# first and the sim second, or not at all until Balance. The
   sim's job at this stage is degenerate-loop and dead-card detection, which
   can run on the sheet draft without a full engine mirror. **Replaces**
   sim-first, and cuts the two-engine tax out of the loop that needs taste,
   not numbers.
8. **Merge authority for plumbing.** Install the GitHub CLI. Claude opens PRs
   and merges the ones that touch only registers, indexes, logs, lints and
   records when CI is green, and stacks content PRs for you in one batch per
   sitting. **Replaces** you merging 111 PRs in four days. Main's push rule
   stays.
9. **Rename the seat's outputs.** ADVANCE becomes PLAYABLE and RETURN becomes
   NOT PLAYABLE, and the pair read is described as a defect-and-legibility
   read in the packet header. Same instrument, honest label. **Replaces** a
   word that reads as approval.
10. **One register for engineering, one for your picks, and nothing else
    mints ids.** BACKLOG keeps EB ids. QUEUE holds only A, B and C picks, with
    defaults, and is empty most of the time. The M series stops; a pick is
    named by its packet section until it is ruled and then by its R number.
    **Replaces** three id series and the collisions between them.

## 8. What stays exactly as it is

The lints, the tests, the soak, the bite-check, the two-family independence
rule and authorship recording, stamped worlds and the re-baseline for
anything that ships, blind grading for any number that will be quoted,
records struck rather than rewritten, the art ladder, the naming lint, the
worktree rules, and the rule that Claude never deploys without a go.

## 9. The picks

Numbered, with the default I will build on unless you say otherwise.

1. **The three-stage gate (change 1) and the fun gate (change 2).** (1)
   *Adopt both; the Klee brief is the first Paper artefact, and the first
   Prototype gate is two fights by you on a Klee `+proto` build once the sheet
   is drafted* [default]. (2) Adopt the stages but keep you out of play; find
   another fun instrument. I have none to offer and neither does the
   machinery.
2. **Default-and-veto (changes 3 and 4).** (1) *Adopt as written* [default].
   (2) Adopt for D and E only, keep F returning.
3. **Split LAW (change 6).** (1) *Move character identity into the briefs and
   demote the charter to a checklist* [my recommendation; a LAW amendment, so
   yours]. (2) Keep LAW as is and treat every kit change as an amendment.
4. **Prototype in C# first (change 7).** (1) *Yes, sim only at Balance*
   [default]. (2) Keep sim-first.
5. **Merge authority (change 8).** (1) *Claude merges plumbing PRs on green
   CI, you merge content in batch* [default]. (2) Claude merges everything on
   green CI. (3) Keep as is.
6. **Prose diet numbers (change 5).** (1) *Two-page memos, 150-line STATE,
   1,000-line packet split rule, ruled packets leave active the same day*
   [default]. (2) Different numbers, which I will take from you.

## 10. What this document does not do

It does not change a rule, move a file, or mint anything. It does not review
the art pipeline, the understudy bridge, or the C# build, all of which work.
It does not decide Kokomi's brief, which is next, and it does not decide the
companion layer, which waits for both briefs. It is the assessment you asked
for, with the numbers behind it.
