# P-ledger — every Class-P item landed under R119, with its veto handle

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status: REGISTER. Zero design authority.** Mandated by the Class-P charter
(`docs/class-p-charter-2026-08-06.md` §3, SIGNED per R119): one row per landed
Class-P item — what, the one-sentence predictability argument, the revert
handle. **The veto is the consent structure:** any row [USER] flags in a digest
reverts by its handle, no argument, no re-litigation. Silence after digest
ratifies the batch.

**Format is load-bearing.** `tools/lint_p_ledger.py` fails the suite when a row
(a `## ` section carrying a `**Handle:**` field) lacks a five-line
`**Attestation:**` block, or when a handle commit touches a file owned by a
[USER]-gated register (definition: that lint's header). Item ids (`C-1`…)
are the P-A inventory's, `review/stage-clear/class-p-candidates.md`.

**Batch 1 — the purge swarm (P-B), 2026-08-06.** Digest:
`review/stage-clear/combined-digest-draft.md`, P-B section. Objection window
opens when P-C's digest is delivered.

---

## C-1 — `unmodelled_starting_relics` is KEPT (queue 10.4)

**What:** the queue's yes/no is answered YES as a recorded answer, not a
change: the sentinel key's spelling is accurate (three characters' starter
relics are genuinely inexpressible in tier0 vocabulary; the name watches the
COUNT while disclaiming the effect). Queue row struck with the reasoning.
**Predictability:** no reasonable owner renames an accurate spelling to
manufacture three standing false sentinel findings.
**Handle:** `2489d26`
**Attestation:**
1. Zero design authority — a tool-internal YAML key name; no card, number, player-facing text, law, or money.
2. Truth-restoring/hygiene — confirms an accurate name; the revert alternative manufactures a standing false finding for three characters.
3. Reversible in one commit — blast radius: one queue-row closure; the spelling itself does not change.
4. Predictability — sitting-prep §10.4's own text states the trade; no judgment beyond reading it.
5. No gate collision — sentinel tooling; not escrowed, not pre-registered, not a measurement surface.

## C-2 — the P1.5 acceptance clause meant `understudy/trace_replay.py` (queue 10.5)

**What:** the recorded ambiguity is resolved from the P1.5 record's own stated
evidence — *"reconstruction only, no rules retyped"* describes the recording
comparator, not the engine driver. Queue row struck; one dated additive
annotation on the P1.5 record (frozen prose untouched). Neither module changes.
**Predictability:** the record's own analysis already points one way and only
declined for lack of authority, which R119 supplies.
**Handle:** `b6e8549`
**Attestation:**
1. Zero design authority — a record clarification about which existing file a past clause named; neither module changes.
2. Truth-restoring — resolves a recorded ambiguity from the record's own stated evidence.
3. Reversible in one commit — queue row + one dated additive annotation on the P1.5 record (a stated widening of P-A's attested radius, ordered by the P-B dispatch).
4. Predictability — the clause text is decisive on the record's own analysis; no taste or play memory involved.
5. No gate collision — the P1.5 gate package is countersigned and closed; nothing rides on the name.

## C-3 — Punch Off reclassified SUSPECTED-OURS → game-side/spine-side (queue 10.6)

**What:** `EB-1`'s owner note flips and the crash memo gains a dated
reclassification banner, per the memo's own evidence (zero signal connects in
our mod; the named signal exists only in native spine-godot; our patch is a
postfix past the raising frame). The rotation caveat is preserved verbatim;
the acceptance form (seed `8B97LMCL2F`) stays recorded.
**Predictability:** with zero evidence of our code in the trace, any
reasonable owner reclassifies an attribution the record itself marks
inferred-not-observed.
**Handle:** `d558264`
**Attestation:**
1. Zero design authority — a defect-attribution record; no behaviour changes anywhere.
2. Truth-restoring — corrects an inferred attribution to match the gathered evidence.
3. Reversible in one commit — EB-1 note, additive memo banner, queue row; nothing else.
4. Predictability — the memo's evidence chain is nine offline-re-runnable checks, all pointing one way; the caveat is carried so nothing is overclaimed.
5. No gate collision — not gated, not escrowed, not a measurement surface; the animation stream keeps the watch.

## C-4 — §2.2a's phantom citation replaced by the census (queue 10.9)

**What:** the false evidence parenthetical in the design principles' §2.2a
(the act-3 Ancient stun reward, which no extraction contains) is struck —
kept visible, R101b — and replaced by the true, stronger citation: the
official pool has no player-applied stun/skip/intent-delay anywhere
(`docs/archive/zhongli-dossier-2026-08-05.md` §2). The rule's content and force are
unchanged. Opens `docs/registry/excision-log.md` (Clear-the-Stage rail 3)
with this strike as row E-1.
**Predictability:** no owner keeps a citation to a card that does not exist
when a stronger true citation is in hand.
**Handle:** `e52fae2`
**Attestation:**
1. Zero design authority — only the rule's stated evidence changes, never its content or force.
2. Truth-restoring — removes a false citation from a LIVING law doc; the census is the citable superseder.
3. Reversible in one commit — one struck passage, dated note, excision-log row, queue row.
4. Predictability — queue row 10.9 asked to authorize exactly this repair; the stronger citation was already identified.
5. No gate collision — not gated; not a number; not a measurement surface.

## C-7 — the atlas spells the vendor path at all five shorthand sites

**What:** `docs/atlas/vendor-sts2-mcp.md` cited the vendor wire-contract docs
as bare `docs/raw-simplified.md:<n>` / `docs/raw-full.md:<n>` (paths that
resolve to nothing) while spelling `vendor/STS2_MCP/docs/…` correctly in its
own reading list; all bare tokens now carry the full path. Count correction
against the inventory: the mechanical sweep finds **five** bare tokens, not
six (one line carries two).
**Predictability:** no owner prefers a pointer that resolves to nothing when
the correct expansion is stated in the same file.
**Handle:** `32163cf`
**Attestation:**
1. Zero design authority — path spelling in a code-map doc.
2. Truth-restoring — repairs stale/ambiguous pointers in a LIVING doc against the doc's own reading list.
3. Reversible in one commit — five token edits in one file.
4. Predictability — the correct expansion is stated in the same file; no judgment.
5. No gate collision — none; the atlas documents a vendored module.

## C-8 — a live test stops citing a document that never existed

**What:** `tier0/tests/test_card_play_hook_guards.py` cited
`docs/coop-no-sim-backstop.md` — a chat-memory topic name that was never a
repo file. The docstring now points at the in-repo statement of the same fact
(`docs/archive/brief-coop-charter-items.md`) and records the repair. The two frozen
docs repeating the phantom path stay verbatim per rail 1. No assertion
changes.
**Predictability:** no owner keeps a dangling citation in live code when the
same fact has an in-repo home.
**Handle:** `ce85d34`
**Attestation:**
1. Zero design authority — a test docstring comment; no assertion changes.
2. Truth-restoring — removes a citation to a nonexistent document from live code.
3. Reversible in one commit — one docstring passage.
4. Predictability — the fact is untouched and its in-repo home already exists; no judgment.
5. No gate collision — the test's assertions are untouched; not a measurement surface.

## C-9 — the resolver's prose catches up to its own table (R120)

**What:** `docs/registry/identifiers.md` §3's prose said the tier0 ledger
mints through R116 while its own table two paragraphs down records current
maximum R120; the prose figure is corrected (struck, not erased), verified
against `tier0/DECISIONS.md` at current main (R120 is the last heading; no
R121+ exists in the tree).
**Predictability:** the true maximum is checkable in one grep, and the
registry's §14 mandates exactly this class of correction.
**Handle:** `9907f3b`
**Attestation:**
1. Zero design authority — a range figure in the resolver's prose.
2. Truth-restoring — a one-batch-stale miscount, corrected to match the same file's own table and the ledger.
3. Reversible in one commit — one word.
4. Predictability — mechanical grep; no judgment.
5. No gate collision — registry hygiene; nothing gated.

## C-13 — the decisions-status sidecar's 77 UNREVIEWED rows are triaged (queue §4)

**What:** the standing red-pen row asked for one judgment per ruling. The
[USER] status-pass order of 2026-08-06
(`docs/dispatch-2026-08-06-status-pass-order.md`, verbatim) routes it through
Class-P by supplying a decision rule that removes the judgment: **OPERATIVE is
an absence claim** (no citable superseder found, search scope recorded in the
row), **a moved status requires an explicit citation** quoted in the row with
its scope stated, and **arguable supersession is DOUBT** and stays a queue
item. Executed over all 77: **68 OPERATIVE, 6 moved on in-entry dated banners
that name their citing ruling (R84/R87/R96 → R107, R90/R108 → R118, R116 →
R117), 3 DOUBT** (R59, R103, R107 — one queue row, riding `S4-G9`). The five
pre-derived rows are byte-identical. Digest:
`docs/registry/status-pass-digest-2026-08-06.md`.
**Predictability:** the order states the rule and the rule is a search, not a
verdict — every recorded move quotes the banner that makes it, and every row
where the answer needed taste is DOUBT rather than resolved.
**Handle:** `e0b563c`
**Attestation:**
1. Zero design authority — a status column on a record index; no card, number, player-facing text, law, or money moves, and no ruling's text is touched.
2. Truth-restoring — replaces 77 rows of "nobody has read this" with what a full citation search actually found, and says out loud that OPERATIVE means absence-of-citation rather than endorsement.
3. Reversible in one commit — `git revert e0b563c` restores all 77 rows and the header. Blast radius of the follow-up: the generated digest block re-renders with `python tools/gen_decisions_digest.py --write` (tool-owned output, not a hand edit — which is exactly why it rides the follow-up commit and not the handle, keeping the handle clear of every [USER]-gated register); the generator's header prose and `tier0/tests/test_decisions_digest.py`'s honesty clause are **generalized, not weakened** — from "UNREVIEWED rows must render as UNREVIEWED" to "every row renders as its status and the header counts every category", with the UNREVIEWED half still binding the moment a new ruling lands unread.
4. Predictability — the order fixes the decision rule in advance and forbids inference; the six moves each quote a dated banner naming their citer, and the three rows where a reasonable owner could answer differently are recorded as DOUBT, not resolved.
5. No gate collision — the sidecar is not [USER]-gated (the ledger volumes it indexes are, and none is written here), not escrowed, not a pre-registration, and not a measurement surface; the DECISIONS ledgers themselves are untouched apart from the generated digest block, which the generator owns and CI checks.

---

## NOT landed — the doubt set, recorded so the digest can say why (no rows above cover these)

Surfacing commit `20aaaa9` (queue/docket rows only; no resolution acted on).
Doubt disqualifies (charter §2); each stayed or became a queue/docket row with
the doubt named:

- **C-5 / M12(a)** — was SEQUENCED-AFTER-WINDOW; on re-attestation with the
  v6 window closed it **failed test 4 and was downgraded to DOUBT, not
  landed**: the "four cards" premise contradicts the ratified sheet's own
  current statements (`undercurrent` left the cell, `furina-cards.yaml:391–395`;
  `standing_room_only` left the watchlist, `:647`) — the record says three,
  four, and two at once. Doubt named on queue §10 row `M12`.
- **C-6 / M12(b)** — premise false, no action needed: catalyst Kokomi is
  already registered for hydro convergence in two places. Finding recorded on
  `M12`'s row; nothing edited.
- **C-10** — the unbannered Skeleton2D spike doc: choosing the status IS the
  judgment. Minted as `EB-44`.
- **C-11** — 18 archive-internal dead pointers: unrepairable at the citer
  under rail 1; a move-policy input for the Clear-the-Stage R-B track. Minted
  as `EB-45`.
- **C-12** — two never-committed PNGs cited by frozen docs: a fact only the
  primary checkout can see. Minted as user-queue §9 item 5.
