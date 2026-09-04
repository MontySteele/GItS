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

**Balance, gated by measurement.** Accepted rows are re-authored onto the
character's real sheet under a `CONSTANTS_VERSION` bump and deleted from the
prototype surface in the same commit; `EXPERIMENTS.md` binds in full from here
(pre-registration, blind grading, stamps, bands, and the twelve-arm
re-baseline where one is owed). The landing's slate also strikes the `LAW.md`
lines the rulings deprecation audit lists for that kit
(`review/ruled/rulings-deprecation-audit-2026-09-04.md` §3, R256 pick 4).
**Exit:** the re-baseline publishes.
