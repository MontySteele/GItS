## The three-stage gate (Paper / Prototype / Balance)

A kit moves Paper → Prototype → Balance (`CLAUDE.md` §Norms). Each stage asks
for one kind of evidence and exits on it.

**Paper, gated by taste.** Artefacts: the character brief and the sheet drafts,
written to `review/active/<character>-brief-<date>.md` and read against
`docs/current/kit-checklist.md`. No build, no flag, no commands. **Exit:** [USER] has read the brief and ruled its picks.

**A card paper carries its readings.** It lists every reading a builder would
otherwise have to choose: when a condition is checked, what counts as X, how
two effects stack. A build agent that meets a reading the paper does not list
picks one, records it in the provenance note, and flags it in its report.

**Prototype, gated by play.** Rows go on `docs/prototype-surface.yaml` and are
built in **C# first** (next section). Deploy with `tools/deploy_round.py`
(since 2026-09-28 the release build carries the current kits, so no dev
build is needed), run the three-fight soak, then play.
**Measurement law does not bind here:** no prediction slate, no countersign, no
registration, no stamp, no re-baseline, and no number taken off a prototype row
is quotable (LAW, *Design governance*). The evidence is [USER]'s play at a rule
change plus the seats' rounds. A rule that does not survive play is rewritten
and the brief edited in place. **Exit:** the finish line below.

### The loop inside Prototype (2026-09-23)

A seat round answers a question the design has. It runs **only when a rule
changes or a new batch of cards lands**, never to re-read the last round's
fixes, and it uses **two seats** by default (`operations/understudy-seats.md`
has the procedure). Each round opens with the one gameplay question it tests,
about a deck the character can become, not a shelf count.

**The committed record is one page**, in `review/records/<kit>-round-<n>-<date>.md`,
with three parts: **what played well, what did not, what to change.** Raw seat
transcripts stay on disk: `review/qa/` is gitignored for new files. A display
defect a seat hits becomes one line in `BACKLOG.md`, not a paragraph in the
record. No build hashes, stamp disclosures or register cross-references in
the record; git has them.

What to change is the smallest intervention the evidence supports, in this
order: a display or tip corrected, an existing card adjusted, access improved,
two redundant cards merged or one cut, a new capability, a core rule changed.
A card that is added says what it displaced. The starting relic changes only
on a structural fault (the starter does not present the central choice, the
relic is dead in a deck the kit supports, or it makes one strategy the default
winner). Starter basics are never changed.

### Done, for a kit in Prototype (2026-09-23)

**Every kit's pool target is 78 standard draftable cards**, plus its Ancient
rewards and its multiplayer cards. A small pool reads more reliable than a
full one, so a kit is judged for Balance on a pool at or near 78.

**The finish line, for every kit:** the pool reaches (or nearly reaches) 78,
two seats play it, and then [USER] plays one full run. **Fun through act 3
moves the kit to Balance.** If it is not fun, his notes say which part, and
that part is fixed.

- **Klee** (`review/ruled/klee-review-2026-09-23.md`): the pick-1 batch lands
  first (Tripwire, Explosive Frags, Where Did I Put It?, Nova Burst in; five
  shelf cards out; 48 draftable), then the pool grows to 78, then two seats
  and one full run by [USER]. The old three-line calibration gate
  (`review/records/klee-fun-calibration-2026-09-14.md`) is retired.
- **Kokomi** (`review/ruled/kokomi-review-2026-09-23.md`): the Plan-card
  rewrite at 39 cards, two seats, then [USER] plays because her central rule
  changed; the pool then grows to 78.
- **Furina** (`review/ruled/furina-review-2026-09-23.md`): the two Spend rules
  and about ten Stage cards, two seats, then [USER]'s first Stage run; the
  pool then grows to 78.

**Balance, measured on the real game** (`review/active/klee-balance-measurement-2026-10-05.md`, ruled 2026-10-05). The bar is a base character's level: the kit's runs on the base-five baseline seeds (`review/records/base-five-baseline-2026-10-05.md`) reach act 3 as the base five's do, its damage a turn and HP lost by act sit within about 15% of theirs in the fight telemetry, and [USER]'s run says it is fun. Rows stay on `docs/prototype-surface.yaml`; there is no re-authoring and no `CONSTANTS_VERSION` bump, and the sim re-baseline is not the gate. Each balance change states its expected effect in one line in its own paper, graded by the next suite.

**The build is frozen until the metrics are recaptured** ([USER], 2026-10-05: "build is frozen until balance metrics are recaptured - aka we can make prototype changes, but not push them into the release build until the full suite is run"). A Balance kit's cards and rules on `main` (every build and release) do not change between suite runs. Changes to it are made on the staging branch `<kit>-next`, deployed for play and seats as a `+next` build (`tools/deploy_round.py --staging`), and reach `main` in one promotion PR that carries the suite record: the kit on the base-five baseline seeds through act 3 and the telemetry report, each change's one-line prediction graded.

**Exit:** the bar is met on a suite run.

**Solo first, co-op checked (2026-10-06).** A kit is judged on solo play
against the base five; [USER]'s co-op runs read fun and feel, not strength
(he wins any A0 co-op run with base characters). [USER]: "It's fine for
co-op to be easier, but the characters should not be outright weak in single
player and dependent on reactions in a way that makes co-op exponentially
easier." The co-op check is a paired seat round on shared seeds: a kit pair
whose elements react against a base pair (Ironclad + Silent), on the same bar.
