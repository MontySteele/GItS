# Archive

Files retired from the working tree on 2026-10-13 so no agent reads them as
current. Git keeps every one. To read one:

```
git fetch --depth=1 origin cb00ad06135606579f6e0f6237c4565bc1650425
git show cb00ad061:<path>
```

Older history (before 2026-08-06): `git show pre-simplification-2026-08-06:<path>`.
Ruled and built papers were not removed; they moved to `review/ruled/`.

| path | why it was retired |
|---|---|
| `docs/current/calibration/` (calibration-notes, klee-real-battery-calibration, sprint-sim-hygiene-log-2026-07-29) | sim calibration bands, retired as gates 2026-10-01 |
| `docs/current/characters/` (furina, klee, kokomi and roster identity records; klee-character-design; furina-kickoff-v0.1; kokomi-kickoff-v1) | first-era kit identities and kickoffs; each kit is re-founded and its brief in `review/active/` governs |
| `docs/current/operations/register-ids.md` | the retired EB/M id machinery; CLAUDE.md norms replace it |
| `docs/current/rationale/` (README, serenitea-g3-ci-proposal, serenitea-g4-session-isolation) | 2026-08 CI and worktree proposals; `operations/ci.md` and `operations/worktrees.md` govern |
| `docs/current/research/companion-value-vs-colorless-study.md` | superseded by `research/colorless-anchor-2026-08-30.md` |
| `docs/current/research/ironclad-brief-calibration-2026-09-01.md` | one-off brief-format exercise |
| `docs/current/roster/roster-anchor-v14-v6-2026-08-06.md` | sim anchor table from the calibration era |
| `docs/current/watch-register.md` | watch list for Furina v1 quantities |
| `docs/current/workstreams.md` | frozen 2026-09-23 narrative; `STATE.md` replaces it |
| `docs/furina-fanfare-parity-vectors.json`, `docs/kurage-affordability-vectors.json` | vectors for retired Furina v1 and Kurage Memory mechanics; nothing read them |
| `docs/notes/{fontaine,inazuma,mondstadt}-companions-provenance.md`, `docs/notes/{furina,klee,kokomi}-{cards,upgrades}-provenance.md` | comments from the old per-kit sheets, deleted in legacy cleanup stages 5-6 |
| `docs/roster-codegen.md` | pre-prototype-surface codegen contract; `operations/codegen.md` replaces it |
| `docs/track-a-kickoff-brief.md` | executed 2026-08-04 Axis-Validity brief |
| `review/active/furina-stage-brief-2026-09-08.md` | Furina v1 Stage brief, frozen 2026-10-05 |
| `review/active/klee-turn-one-paper-2026-10-08.md` | superseded by `review/ruled/klee-design-review-2026-10-08.md` |
| `review/active/kokomi-growth-powers-2026-10-10.md` | Casket-count growth Power; the Casket count was retired 2026-10-12 |
| `review/dispatch3/` (49 files) | August 2026 research lanes: public-mod patterns, engine sockets, animation, art batches |
