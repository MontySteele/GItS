# "Clear the Stage" — /docs general refactor charter

> **SIGNED 2026-08-06 — §6 is resolved AUTHORIZE, all tracks including R-D.**
> [USER] delivered this charter with the verbatim framing line: *"And another
> cleanup pass after thatg - also fully AUTHORIZEd:"* (typo preserved). Against
> §6's three-option form, "fully AUTHORIZEd" = **AUTHORIZE** — R-A/B/C/E and
> the R-D ledger volumization all proceed. Recorded as part of ruling R119
> (`tier0/DECISIONS.md`) with the verbatim framing quoted.
>
> **Sequencing, per the charter's own §5 non-goals:** the refactor does not
> operate inside the open v6 measurement window — execution begins after the
> v6 re-baseline sweep is green (in flight this wave as Tracks V/M). The
> charter body below is [USER]'s text, verbatim — including its own
> pre-signature "Nothing here operates until [USER] signs §6" sentence, which
> is kept as delivered and is discharged by this banner, not rewritten (R101b).

# "Clear the Stage" — /docs general refactor charter (DRAFT)

> **Lifecycle: LIVING while the refactor operates.** Companion to the
> Class-P charter; the two swarms share an inventory pass and a digest.
> Directive, verbatim ([USER], 2026-08-06): *"Archive old docs; clean up
> active docs to remove stale sections; generally simplify what remains so we
> do not have a million lines of stale decisions contaminating things."*
> **Nothing here operates until [USER] signs §6.**

## §1 — What the diet did and what it deliberately did not

Track Z gave every file a lifecycle status (59 LIVING / 205 REFERENCE / 66
ARCHIVED), retired five registers to pointers, and consolidated open items
into two homes. It did **not** move files, prune sections, or touch the
decision ledgers — it weighed every page and moved none. This charter is the
move. The contamination [USER] names is real and has a mechanism: a reader
(human or agent) greps `docs/` and hits superseded prose with equal weight
to operative law. The fix is separation, not deletion.

## §2 — Laws this refactor operates under (non-negotiable rails)

1. **Nothing is rewritten in a frozen record.** REFERENCE and ARCHIVED text
   moves whole or stays; its words never change. Simplification happens by
   relocation and by pointers, never by editing history.
2. **Stale-by-citation only.** A section in a LIVING doc may be cut only if
   a specific later ruling, doc, or landed change **explicitly supersedes
   it, cited in the excision log**. "This looks outdated" is inference;
   inference → surface as a queue/docket row, never cut. This is the same
   discipline as Class-P test 4: doubt disqualifies.
3. **Every excision is logged** (`docs/registry/excision-log.md`): file,
   section, superseding citation, commit. Git history plus the log means
   nothing is ever unrecoverable or silently gone.
4. **Citation integrity is a suite gate.** The citation lint (now widened
   per Q15) must be green after every move; moves repoint citations in the
   same commit.
5. **Zero design authority.** No ruling's content changes, no number, no
   law. If simplifying a passage would change what it permits or forbids,
   it is not simplification.

## §3 — Tracks

**R-A — Inventory + citation graph** (shared with the purge swarm's P-A).
Build the who-cites-whom map across `docs/`, `review/`, `tools/`, tests,
and both DECISIONS files. Output: per-file in-degree, so demotions know
what they break before they break it.

**R-B — REFERENCE demotion.** Move REFERENCE files with no live citers (or
citers repointable in the same commit) from `docs/` root into
`docs/archive/`, verbatim, banner noting the move date. Target state: the
root holds LIVING docs, the registries, the dockets, and nothing else.
Acceptance: `docs/*.md` ≤ 15 files (from 104 today), every move citation-
green.

**R-C — LIVING prune.** For each of the 59 LIVING docs: strike sections
superseded-by-citation (rail 2), replace restated decisions with one-line
pointers to the ledger (finishing what Z-6 started), collapse duplicated
background into the resolver. Anything the prune is *unsure* is operative
becomes a DOUBT row, not a cut. Acceptance: no LIVING doc restates a ruling
it can point to; excision log complete.

**R-D — Ledger volumization (the "million lines" itself).** The DECISIONS
files are the spine and are append-only; they are also now long enough that
stale entries dominate any read. Proposal, in one move per ledger:
- Freeze closed ranges into append-only archive volumes
  (`tier0/DECISIONS-archive-R1-R99.md`, etc.), verbatim.
- The live file keeps: open/recent rulings, plus a **generated current-law
  digest** — one line per still-operative ruling, produced by a tool from
  the volumes, never hand-edited (generated = not a place truth can drift).
- `registry/identifiers.md` §1 resolves every R-number to its volume; the
  CI duplicate-number lint runs across volumes as one namespace.
- Cross-session note posted before this lands (shared-schema change: every
  agent and tool that greps the ledger must learn the volume layout).
This is the only track that changes how the spine is *read*, so it is
**separately gated in §6** — decline it and R-A/B/C still deliver most of
the cleanup.

**R-E — Acceptance + digest.** Before/after counts (files, lines, LIVING
budget), full lint suite, excision log review, and a one-page plain-language
digest to [USER]: what moved, what was cut and on whose supersession, what
was surfaced instead of cut. Vacation test applies.

## §4 — Interplay with the Class-P purge

Most refactor actions are Class-P-shaped (hygiene, reversible, predictable)
and ride the same attestation + P-ledger + digest + veto machinery. The
charters differ in one place: the refactor adds rail 2 (stale-by-citation),
which is *stricter* than Class-P test 4 — a cut needs not just a
predictable answer but a citable superseder. Both swarms share P-A/R-A and
emit one combined digest.

## §5 — Non-goals

No deletions from git history; no edits inside REFERENCE/ARCHIVED text; no
changes to YAML design sheets (they are data, not docs, per the index); no
touching anything inside the open v6 measurement window; no "improving"
prose whose meaning is load-bearing; no renumbering, ever.

## §6 — The authorization [USER] signs

Two words, or one:
- **AUTHORIZE** — all tracks including R-D (ledger volumization).
- **AUTHORIZE-EXCEPT-D** — R-A/B/C/E proceed; the ledgers stay monolithic
  and R-D returns as its own proposal later.
- **DECLINE** — nothing moves.
