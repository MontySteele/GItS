## The three-stage gate (Paper / Prototype / Balance)

A kit moves Paper → Prototype → Balance (`CLAUDE.md` §Norms). Each stage asks
for one kind of evidence and exits on it.

**Paper, gated by taste.** Artefacts: the character brief and the sheet drafts,
written to `review/active/<character>-brief-<date>.md` and read against
`docs/current/kit-checklist.md`. No build, no flag, no commands. **Exit:** [USER] has read the brief and ruled its picks.

**Prototype, gated by play.** Rows go on `docs/prototype-surface.yaml` and are
built in **C# first** (next section). Deploy with
`klee-mod\build\deploy_proto.ps1`, run the three-fight soak, then play.
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
  first (Tripwire, Explosive Frags, Where Did I Put It?, Big Bounce in; five
  shelf cards out; 48 draftable), then the pool grows to 78, then two seats
  and one full run by [USER]. The old three-line calibration gate
  (`review/records/klee-fun-calibration-2026-09-14.md`) is retired.
- **Kokomi** (`review/ruled/kokomi-review-2026-09-23.md`): the Plan-card
  rewrite at 39 cards, two seats, then [USER] plays because her central rule
  changed; the pool then grows to 78.
- **Furina** (`review/ruled/furina-review-2026-09-23.md`): the two Spend rules
  and about ten Stage cards, two seats, then [USER]'s first Stage run; the
  pool then grows to 78.

**Balance, gated by measurement.** Accepted rows are re-authored onto the
character's real sheet under a `CONSTANTS_VERSION` bump and deleted from the
prototype surface in the same commit; `EXPERIMENTS.md` binds in full from here
(pre-registration, blind grading, stamps, bands, and the twelve-arm
re-baseline where one is owed). The landing's slate also strikes the `LAW.md`
lines the rulings deprecation audit lists for that kit
(`review/ruled/rulings-deprecation-audit-2026-09-04.md` §3, R256 pick 4).
**Exit:** the re-baseline publishes.
