# Dispatch — the decisions-status sidecar goes through Class-P triage

> **Lifecycle: REFERENCE once landed.** Drafted 2026-08-06 in chat; the order
> below is [USER]'s, verbatim, from the same channel. Zero new design authority
> beyond the order itself: it directs a Class-P (paperwork) pass over an
> existing register and creates no ruling, number, or law. House style applies:
> P-ledger machinery per the signed Class-P charter (R119), full attestation,
> per-batch digest with the no-argument veto, suite green at every boundary.

**[USER], verbatim (2026-08-06):**

> *"Status-pass order: run the decisions-status sidecar through Class-P triage.
> For each UNREVIEWED row: OPERATIVE if no citable superseder exists anywhere in
> the ledgers, errata, or landed changes; SUPERSEDED only on an explicit
> citation, recorded in the row. Full attestation per row, P-ledger machinery,
> digest + veto as usual. Rows where supersession is arguable — partial
> amendments, rulings whose scope a later ruling narrowed without naming it —
> are DOUBT and go to the queue. Expected shape: the large majority auto-resolve;
> the DOUBT set should be short, and it rides the G9 sitting rather than standing
> alone."*

---

## What the order fixes, and what it does not

The sidecar (`tier0/decisions-status.tsv`) was minted by Track R-D of "Clear
the Stage" with one row per ruling R39–R120 across every volume. Five rows
carried a status derived mechanically from an explicit strike or banner
(R54/R55/R56 → R56/R73, R88 → R118, R102 → R113); the other **77 said
`UNREVIEWED`**, which the file's own header defines as *"the red-pen pass has
not read this row"*, nothing more. The standing queue row asking for that pass
is `docs/registry/user-queue.md` §4, "Decisions-status sidecar red-pen".

This order routes that pass through Class-P rather than through the [USER]
gate, and it supplies the decision rule that makes it Class-P at all:

- **OPERATIVE is the default and it is an absence claim, not a judgment.** The
  verdict is "no citable superseder was found", with the search scope recorded
  in the row. It asserts nothing about whether a ruling is wise, current in
  spirit, or worth re-opening.
- **SUPERSEDED requires a citation.** A later ruling naming the R-number, in
  strike/amend/discharge/override language, recorded in the row with a short
  locating quote. No inference, no "obviously overtaken".
- **DOUBT is the pressure valve, and doubt disqualifies** — exactly the charter
  §2 rule. A row where supersession is arguable stays unresolved and becomes a
  queue item with its reason named.

The order also states the expected shape in advance — large majority
auto-resolve, DOUBT short — which is a falsifiable prediction about the pass
and is graded in its digest.

## Sequencing

The DOUBT set **rides the G9 sitting** rather than standing alone as its own
ask: a handful of arguable-supersession rows is not worth a sitting of its own,
and the sitting that is already scheduled can take them as one item.

*Identifier resolution, recorded because the order uses the bare form:* "the G9
sitting" is **`S4-G9`**, the ratification batch (`docs/registry/user-queue.md`
§2, OPEN; `review/ledger-audit/hygiene-report.md` G9; backlog §3 item 9). It is
the only open `G9` in the tree. Resolver: `docs/registry/identifiers.md` §2.1.
