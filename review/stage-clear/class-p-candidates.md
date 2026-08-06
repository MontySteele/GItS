# Class-P candidate sweep + five-test attestations (P-A, wave 8)

> **Lifecycle: REFERENCE** — findings record of the shared inventory pass
> (P-A, Class-P charter §6, SIGNED per R119). **Surfacing only.** Nothing was
> resolved, landed, or edited by this pass — every attestation below is a plan
> for the execution swarm (P-B), which is gated on the v6 measurement window
> closing. A PASS here is a recommendation with its attestation pre-written,
> not an action taken.

**Sweep scope, as chartered:** `docs/registry/user-queue.md` (all sections),
`docs/dockets/engineering-backlog.md` (EB-1…EB-43), the five REFERENCE husk
registers the queue names (`backlog-2026-07-29.md`, `open-playtest-items.md`,
`missed-requirements.md`, `sitting-prep-2026-08-05.md`,
`surplus-week-manifest-2026-08-05.md`), plus the dead citations the graph
exposed mechanically (`citation-graph.tsv`). The charter's seed list is
re-attested below, not assumed.

**Never-Class-P screen applied to the whole queue first.** Everything in
queue §2 (S4 gates), §4 (sittings), §7 (table time), §8 (art) is taste,
PROPOSED-number ratification, bands/anchors, probe countersigns, play memory,
or already [USER]-gated — none swept further. The open §5 rows other than the
seeds: 10.10 is awareness-only (no ask, nothing to do); 10.14 is a read (play
memory). Queue §1's open row Q18 is a probe countersign (never eligible).
EB-1…EB-43 are *routed engineering work needing no ruling* — Class-P is not a
work permit and none of them is a paperwork resolution, so no EB row is a
candidate; the sweep found no EB row that is secretly a queue-shaped
paperwork item. The v6 measurement window is OPEN while Track M runs:
anything touching a combat/shop measurement surface is DOUBT-by-gate-5 and is
marked **SEQUENCED-AFTER-WINDOW**, never plain PASS.

Verdict key: **PASS** = all five tests, no doubt. **DOUBT** = stays a queue
row, failing/doubtful test named. **SEQUENCED-AFTER-WINDOW** = tests 1–4
clean, gate 5 blocked only by the open v6 window.

---

## C-1 — queue §5 row 10.4: keep the `unmodelled_starting_relics` spelling (seed, re-attested)

Recommendation: **KEEP** (the "yes" branch of the row's own yes/no).
Fact base: `tools/patch_sentinel.py` + `tier0/tests/test_patch_sentinel.py:148`
— Defect/Necrobinder/Regent starter relics (orb / pet / Stars) are genuinely
inexpressible in tier0 vocabulary; the spelling keeps the relic COUNT watched
while explicitly not claiming the effect is modelled. The name is accurate.

1. Zero design authority — a tool-internal YAML key name; no card, number, player-facing text, law, or money.
2. Truth-restoring/hygiene — confirms an accurate name; the alternative (revert) manufactures a standing false finding for three characters.
3. Reversible in one commit — blast radius: closing one queue row + a P-ledger row; the spelling itself does not change.
4. Predictability — no reasonable owner renames an accurate spelling to create three false sentinel findings; sitting-prep §10.4's own text states the trade.
5. No gate collision — sentinel tooling; not escrowed, not pre-registered, not a v6 measurement surface.

**Verdict: PASS.**

## C-2 — queue §5 row 10.5: which module `UND-P1.5`'s acceptance clause meant (seed, re-attested)

Recommendation: **CONFIRM `understudy/trace_replay.py`**.
Fact base: `docs/sprint-understudy-p15-log-2026-08-05.md` ("The reader"
section) — the clause's own words are *"reconstruction only, no rules
retyped"*, which describes `trace_replay.py` (compares two recordings) and
not `understudy/replay.py` (drives an engine through the actions). The record
flagged the naming for red pen but its stated evidence points one way.

1. Zero design authority — a record clarification about which existing file a past clause named; neither module changes.
2. Truth-restoring — resolves a recorded ambiguity from the P1.5 record's own stated evidence.
3. Reversible in one commit — one annotation on the record's queue row + P-ledger row; both modules untouched.
4. Predictability — the clause text is decisive on the record's own analysis; no taste or play memory involved.
5. No gate collision — the P1.5 gate package is countersigned and closed; nothing rides on the name.

**Verdict: PASS.** (Honesty note: the P1.5 log called this "a real question"
and deliberately did not decide — but the question it declined was one of
authority, not of evidence, and Class-P now supplies exactly that authority.)

## C-3 — queue §5 row 10.6: Punch Off reclassification SUSPECTED-OURS → game-side (seed, re-attested)

Recommendation: **RECLASSIFY** (yes).
Fact base: `docs/punch-off-crash-memo.md` — static reading found zero signal
connects in our mod and no frame in the recorded trace names our code; the
OURS attribution was inferred, never observed. Note carried either way, per
the row itself: the 2026-08-04 crash log has rotated out; the memo's
quotations are the surviving copy; the §6 repro script is hand-session-shaped.

1. Zero design authority — a defect-attribution record (`EB-1`'s owner note + memo status line); no behaviour changes anywhere.
2. Truth-restoring — corrects an attribution the record itself marks as inferred-not-observed to match the gathered evidence.
3. Reversible in one commit — blast radius: `EB-1` note, memo status, queue row; the acceptance form (seed `8B97LMCL2F`) stays recorded.
4. Predictability — with zero evidence of our code in the trace, any reasonable owner reclassifies; the rotation caveat is preserved verbatim, so nothing is overclaimed.
5. No gate collision — not gated, not escrowed, not a measurement surface; the animation stream keeps the watch.

**Verdict: PASS.**

## C-4 — queue §5 row 10.9: §2.2a citation repair (seed, re-attested)

Recommendation: **AUTHORIZE the citation repair** (yes). The rule is untouched.
Fact base: sitting-prep §10.9 — the design principle justifies stun scarcity
via "an act-3 Ancient reward at 3 energy + Exhaust"; the 440-card extraction
contains no such card, and the dossier's §2 census found NO player-applied
stun/skip/intent-delay in the official pool. The correct repair replaces the
false citation with the census, which *supports the rule more strongly* than
the phantom card did.

1. Zero design authority — the rule's content and force are unchanged; only its stated evidence changes.
2. Truth-restoring — removes a false citation from a LIVING law doc, replacing it with evidence that exists (rail 2 satisfied: the dossier §2 census is the citable superseder).
3. Reversible in one commit — one passage in `teyvat-spire-design-principles.md`, dated note, excision-log row.
4. Predictability — no owner keeps a citation to a card that does not exist when a stronger true citation is in hand.
5. No gate collision — not gated; not a number; not a measurement surface.

**Verdict: PASS.**

## C-5 — M12 confirm (a): the owed convergence cell is four cards, not three (seed, re-attested)

Recommendation: record (in `docs/dockets/watch-items.md`, the LIVING register)
that the owed hydro+cryo convergence cell is defined over **four** cards —
`undercurrent`, `rain_of_roses`, `guest_neuvillette_judgment` (per
`docs/red-pen-2026-07-26.md` "The convergence cell was NOT run"), plus
`standing_room_only` (per the ratified watchlist note at
`docs/furina-cards.yaml:391/:776-779`). The tracker doc itself is REFERENCE
(frozen) — the correction lands as a register row, never as an edit to it.

1. Zero design authority — records cell membership that ratified sheet text already states; no number, no card behaviour.
2. Truth-restoring — stops a future builder constructing the cell over three cards when the ratified sheet says four.
3. Reversible in one commit — one watch-items row + P-ledger row.
4. Predictability — follows mechanically from the ratified watchlist addition; charter's own seed argument re-verified against the sheet.
5. Gate collision — **the v6 measurement window is OPEN.** The cell is a combat-measurement instrument definition; 10.3's Never-eligible precedent ("a definition a drafter metric feels") is adjacent, and the house instruction for this wave is that combat-measurement surfaces wait.

**Verdict: SEQUENCED-AFTER-WINDOW** (tests 1–4 attested clean; gate 5 waits
for the v6 re-baseline sweep to go green, then P-B may land it under this
attestation unchanged).

## C-6 — M12 confirm (b): catalyst-Kokomi's missed hydro-convergence listing (seed, re-attested)

The charter's seed says this "follows mechanically from already-ratified
rulings" (R52 ruled her a catalyst; the claim is she was never added to the
hydro-convergence watchlist). Re-attestation **found the premise unclear**:
`docs/archive/kokomi-roster-v0.1-report.md` §5 *already registers* "Hydro
convergence: catalyst Kokomi + the existing hydro/cryo convergence cells
(Furina redpen flag 8)", and `docs/kokomi-cards.yaml:205` carries a per-card
watchlist comment. Whether an operative watchlist home exists that is missing
her — and which register that is (the archived registration? the frozen
red-pen cell? a sheet comment? watch-items?) — is not decidable mechanically
from the record this pass could read.

1. Zero design authority — yes (a watchlist listing).
2. Truth-restoring — only if the "missed" premise is true; the archived registration appears to already list her.
3. Reversible — yes, one register row.
4. Predictability — **FAILS-AS-DOUBT**: deciding which register is the operative watchlist home, against an archived registration that already names her, needs a judgment call; per §2, an attestation that itself required a judgment call disqualifies.
5. No gate collision — same v6-window adjacency as C-5, compounding the doubt.

**Verdict: DOUBT (test 4; gate 5 adjacent).** Stays where it is (queue §10
row M12); the doubt is the finding.

---

## Graph-derived candidates (the charter's "any further miscounts, stale pointers, or dead citations")

## C-7 — atlas shorthand cites `docs/raw-full.md` / `docs/raw-simplified.md`, which do not exist

`docs/atlas/vendor-sts2-mcp.md` (LIVING) cites the vendor wire-contract docs
as bare `docs/raw-simplified.md:15` etc. in six places, while spelling the
true path `vendor/STS2_MCP/docs/raw-simplified.md` correctly in its own
reading list. Fix: spell the full vendor path at the six shorthand sites.

1. Zero design authority — path spelling in a code-map doc.
2. Truth-restoring — repairs a stale/ambiguous pointer in a LIVING doc; the doc's own §"reading list" is the citable correct form.
3. Reversible in one commit — six line edits in one file.
4. Predictability — no owner prefers a path that resolves to nothing; the correct expansion is stated in the same file.
5. No gate collision — none; the atlas is documentation of a vendored module.

**Verdict: PASS.**

## C-8 — a live test cites `docs/coop-no-sim-backstop.md`, which has never been a repo file

`tier0/tests/test_card_play_hook_guards.py:13` states its WHY as "(there is
no C# test project (docs/coop-no-sim-backstop.md))". The fact is true and
load-bearing; the citation is to a document that never existed in the repo
(it is a chat-memory topic name). Two frozen docs repeat the phantom path
(`brief-coop-charter-items.md`, `sprint-bugfix-log-2026-07-29.md`) and stay
verbatim per rail 1. Fix: repoint the test docstring to the in-repo statement
of the same fact, `docs/brief-coop-charter-items.md` (which asserts it in its
own §"co-op has no sim backstop" framing), or state the fact without a path.

1. Zero design authority — a test docstring comment; no assertion changes.
2. Truth-restoring — removes a citation to a nonexistent document from live code.
3. Reversible in one commit — one docstring line.
4. Predictability — no owner keeps a dangling citation when the same fact has an in-repo home; the fact itself is untouched.
5. No gate collision — the test's assertions are untouched; not a measurement surface.

**Verdict: PASS.**

## C-9 — identifiers.md §3 prose is one batch stale ("R39–R116 in `tier0/DECISIONS.md`")

`docs/registry/identifiers.md` §3's opening paragraph still says the tier0
ledger mints "R39–R116" while the very next table row correctly records
R81–R120 with current maximum R120. Fix: correct the prose figure to R120
(the registry's §14 "Keeping this file true" mandates exactly this class of
correction; the file is LIVING and is the resolver of record).

1. Zero design authority — a range figure in the resolver's prose.
2. Truth-restoring — a miscount, corrected to match the same file's own table and the ledger.
3. Reversible in one commit — one word.
4. Predictability — the true maximum is checkable in one grep; no judgment.
5. No gate collision — registry hygiene; nothing gated.

**Verdict: PASS.**

## C-10 — `docs/animation-spike-skeleton2d-kokomi-2026-08-06.md` carries no lifecycle banner

The Z-1 law says every `docs/` `.md` carries a status header; this Track AN
findings note has none (the other four unbannered root files are the three
§15.5 index-only generated files plus the payoff-reach re-registration draft,
whose deliberate `Lifecycle: DRAFT` banner is its own, countersign-gated
state and is not touched by this pass).

1. Zero design authority — a status banner.
2. Truth-restoring — brings the file under the diet's own law.
3. Reversible — one line.
4. Predictability — **FAILS-AS-DOUBT**: choosing the status is the judgment. REFERENCE (a findings record, §15.3's class) is likely, but EB-42 makes the Skeleton2D spike a live Code sprint, and the LIVING budget grants "one charter per active sprint" — whether this doc is that sprint's charter or a closed record depends on Track AN's state, which this pass cannot see.
5. No gate collision — none.

**Verdict: DOUBT (test 4).** Surface to the execution swarm with the status
question attached.

## C-11 — 18 archive-internal dead sibling pointers (policy question, not a fix)

`docs/archive/*` files cite each other at pre-move root paths (18 dead
targets; full list in `citation-graph-notes.md`). Rail 1 forbids editing
frozen text, so these are unrepairable at the citer and have been tolerated
since their moves. The only genuine question is for R-B's move policy: accept
the same staleness for the next wave of moves, or leave ledger-/archive-cited
files in place (refactor-plan §R-B takes the second answer for ledger-cited
files).

**Verdict: DOUBT (test 2 — nothing false is being asserted by a frozen
record about the world *as of its date*; test 3 — no one-commit fix exists
that respects rail 1).** Recorded as tolerated staleness; no queue row needed.

## C-12 — two never-committed PNGs and one gitignored mockup are cited by frozen docs

`docs/animation-sprint-2-a3-intake.png` and
`docs/klee-art-hunt-contactsheet.png` (cited by `animation-sprint-2-log.md`
and `tech-debt-audit-2026-07-26.md`) were never committed;
`docs/mockups/salon-stage-d1-mockup-2026-07-28.html` is gitignored. Whether
the PNGs still exist on the primary machine and should be committed is a fact
this worktree cannot see.

**Verdict: DOUBT (test 4 — whether to commit binary evidence is partly an
art/repo-size call; test 2 — cannot verify the artifacts exist to restore).**
Surfaced as a one-line fact question for the primary checkout, not a queue row.

---

## Tally

| Verdict | Count | Items |
|---|---|---|
| **PASS** | 7 | C-1, C-2, C-3, C-4, C-7, C-8, C-9 |
| **SEQUENCED-AFTER-WINDOW** | 1 | C-5 |
| **DOUBT** | 4 | C-6, C-10, C-11, C-12 |

Note: the husk
registers themselves yielded no additional candidates beyond the seeds: their
still-open rows were already migrated to the queue/docket by Track Z, and the
two miscounts the merge train carried (queue §6 items 1–2) were corrected
under R118 before this sweep ran. Sweep coverage caveat, stated honestly: the
five husks were checked via their migrated rows, the Z-3 migration's own
discharge table (`engineering-backlog.md` §8), and the mechanical graph — not
re-read line-by-line; a line-by-line miscount hunt inside frozen husks was
judged low-yield since corrections could not land in them anyway (rail 1).
