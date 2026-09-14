## The three-stage gate (Paper / Prototype / Balance)

A kit moves Paper → Prototype → Balance (`CLAUDE.md` §Norms). Each stage asks
for one kind of evidence and exits on it.

**Paper, gated by taste.** Artefacts: the character brief and the sheet drafts,
written to `review/active/<character>-brief-<date>.md` and read against
`docs/current/kit-checklist.md`. No build, no flag, no register row, no
commands. **Exit:** [USER] has read the brief and ruled its picks.

**Prototype, gated by play.** Rows go on `docs/prototype-surface.yaml` and are
built in **C# first** (next section). Deploy with
`klee-mod\build\deploy_proto.ps1`, run the three-fight soak, then play.
**Measurement law does not bind here:** no prediction slate, no countersign, no
registration, no stamp, no re-baseline, and no number taken off a prototype row
is quotable (LAW, *Design governance*). The evidence is [USER]'s two fights at
a rule change plus the seats' rounds through the funnel. **Exit:** the rules
survive play, or a rule is rewritten and the brief edited by a sentence.

### The loop inside Prototype (2026-09-05)

A round is not a card order. From round 17 on, every round packet and every
pool pass opens with **one gameplay hypothesis** about a deck the character
can become ("Klee can build around preserving one large Bomb, and that
changes which rewards she wants"), never a shelf count ("Cook needs two more
cards"). Each hypothesis is tested two ways, and neither stands in for the
other: an **assembled deck** (`embark --arm` grants, which say whether the
strategy is interesting at all) and the **route to it** (a natural run, which
says whether a player can reach it and whether its pieces earn their place
on the way). The packet's finding names the **smallest intervention** the
evidence supports, in this order: a display or tip corrected, an existing
card adjusted, access improved (rarity, a second copy, a starter seam), two
redundant rows merged or one cut, a new capability added, a core rule
changed. **No row is a legal finding.** A row that is added answers, in the
packet, what it displaced: when a drafter would still take its nearest
neighbour, and whether it made another strategy unnecessary or thinned the
odds of finding an essential piece. The evidence of depth is a seat that
wants different cards, upgrades or sequences in different decks and can
say why; a more elaborate turn is not evidence. Archetype names in a brief
are hypotheses about decks, not compartments with a target count; a
comparison pass on what an expansion displaced precedes any further
addition to that pool. The starting relic changes only on a demonstrated
structural fault: the starter does not present the central choice, the
relic is dead in a deck the kit is meant to support, or its incentive makes
one strategy the default winner.

### Done, for a kit in Prototype (2026-09-14)

A kit's Prototype has no finish line unless one is written, so every round
is one more finding. **Klee's is this:** on two consecutive builds, [USER]'s
three calibration lines (`review/records/klee-fun-calibration-2026-09-14.md`
§2) answer `NOTHING TURN: none`, and the `MOST WANTED TURN` names a
different play on each. A kit that clears it moves to Balance and its pool
may grow; until then no row is added without the decision it adds stated in
one line, and the build carries only the rows the next reading can judge.
The same calibration tests whether the seats can carry the three lines in
[USER]'s place; its §4 says what each result licenses.

**Balance, gated by measurement.** Accepted rows are re-authored onto the
character's real sheet under a `CONSTANTS_VERSION` bump and deleted from the
prototype surface in the same commit; `EXPERIMENTS.md` binds in full from here
(pre-registration, blind grading, stamps, bands, and the twelve-arm
re-baseline where one is owed). The landing's slate also strikes the `LAW.md`
lines the rulings deprecation audit lists for that kit
(`review/ruled/rulings-deprecation-audit-2026-09-04.md` §3, R256 pick 4).
**Exit:** the re-baseline publishes.
