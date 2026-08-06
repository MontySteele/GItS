# Cross-session note — ledger layout change (R-D, Clear the Stage)

> **Lifecycle: REFERENCE** — a posted notice, frozen as posted. Track R-D,
> 2026-08-06, under the "Clear the Stage" charter (SIGNED full-AUTHORIZE
> including R-D, R119) and the plan of record
> `review/stage-clear/refactor-plan.md` §R-D. **Posted before the split
> lands** — this is a shared-schema change: every agent and tool that greps
> the ledger must learn the volume layout.

The note, per the plan's drafted text:

> Ledger layout change (R-D, Clear the Stage): `tier0/DECISIONS.md` now holds
> R100+ only; R39–R99 are verbatim in `tier0/DECISIONS-archive-R39-R99.md`;
> `klee-mod/DECISIONS.md` is unchanged (R73–R80). Resolve any R-number via
> `docs/registry/identifiers.md` §3, which now carries a volume column. Grep
> both `DECISIONS*.md` globs, not the single file. The current-law digest
> block in the live file is GENERATED (`tools/gen_decisions_digest.py`) —
> never hand-edit it. Numbering is unchanged; nothing was rewritten (R101b).

Three riders the plan text implies, spelled out:

- **The D-series entries D2–D5 travel with the range.** They are physically
  interleaved inside R39–R99 (D2 between R65 and R66; D3–D5 between R72 and
  R81) and move byte-identical with it. `DEC-D5` and its clauses still
  resolve — in `tier0/DECISIONS-archive-R39-R99.md`.
- **R1–R38 are not in any volume.** They were never written as headed
  entries; the back-index question stays `docs/registry/user-queue.md` §4 and
  is untouched by the split (no entries were invented).
- **The archive volume is append-only and frozen** — same law as the live
  ledger (a Class-P item may cite it, never write it; the P-ledger lint's
  gated-register glob covers `tier0/DECISIONS*.md`).
