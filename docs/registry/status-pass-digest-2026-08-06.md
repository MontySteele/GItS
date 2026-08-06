# Status-pass digest — what the sidecar now says, and what it refuses to say (2026-08-06)

> **Lifecycle: REFERENCE** — the per-batch digest the Class-P charter §3
> requires for the status pass ordered at
> `docs/dispatch-2026-08-06-status-pass-order.md`. Frozen as delivered.
> P-ledger row and revert handle: `docs/registry/p-ledger.md` item **C-13**.
> Status index: `docs/registry/identifiers.md` §15.

**Read this cold.** `tier0/decisions-status.tsv` is the one-line-per-ruling
index beside the decision ledgers. Until today 77 of its 82 rows said
`UNREVIEWED` — "nobody has read this row". You ordered them triaged under a
rule that makes the pass a search rather than a verdict, and this page is the
consent step: **any row you flag reverts by the handle below, no argument.
Silence ratifies the batch.**

**Handle:** `e0b563c` (the triage commit; `git revert e0b563c` restores all 77
rows, then `python tools/gen_decisions_digest.py --write`).

## Headline

| verdict | count | what it means |
|---|---|---|
| **OPERATIVE** | **68** | No citable superseder was found. **An absence claim, not an endorsement.** |
| **Moved on an explicit citation** | **6** | A dated in-entry banner names a later ruling in amend/override/supersede language. All six are **partial** — the scope is stated and the rest of the entry is explicitly not judged. |
| **DOUBT** | **3** | Supersession is arguable. Not resolved; one queue row, riding `S4-G9`. |

Plus the **5 rows that were already derived** before this pass (R54, R55, R56,
R88, R102) — byte-identical, untouched. Total 82.

**The order's own prediction, graded:** *"the large majority auto-resolve; the
DOUBT set should be short."* 68 of 77 auto-resolved (88%) and DOUBT is 3.
**Both halves hold.**

## The 6 moved rows — every one with its citation

| row | new status | quote fragment locating the citation | scope of the move |
|---|---|---|---|
| **R84** | `AMENDED-BY:R107` | *"THE 'ONLY QUOTABLE ROSTER TABLE' IS ARCHIVED — annotated 2026-08-06 (R107; S4 finding F4)"* … *"the archive rule wins, because it is the later ruling and the general one"* | Only the quotable-table **designation**. R84's three rulings (v11 constants RATIFIED, `_static_power` authorized, fresh 3-act recalculation ordered) are not struck. The table was re-designated again by R118 §2 row 10.2 under v6. |
| **R87** | `AMENDED-BY:R107` | *"GOVERNING CONDITION RE-POINTED 2026-08-06 (R107; S4 finding F1)"* … *"Re-pointed, not released"* | Only item (1)'s **governing condition** (items 1–3 + the fanfare STOP now govern on Track B / `B-G1`). R118 §1 Q7 later re-points the same fence to the narrowed Fanfare-axis form. R87's other three rulings stand. Its separate R102 escrow banner was struck by R113; the 1.8% STOP stands as ratified. |
| **R90** | `AMENDED-BY:R118` | *"[USER] RULING 2026-08-06 — `B-G1` is NARROWED to the Fanfare axis; the other six axes close permanently"* (Q7, *"landed verbatim per R118"*) | Only clause **1b**'s gate — *"only its scope shrinks"*. Clauses 1a (the lint stays a counting tool) and 1c (floors re-derived from canon packages) are not struck. |
| **R96** | `AMENDED-BY:R107` | *"CORRECTION 2026-08-06 (R107; S4 finding F2). The fixture is RE-HOMED … and is no longer an acceptance condition on DRAFTER 13."* | Only item **1**'s acceptance owner — *"Nothing measured is rewritten"*. Items 2 and 3 stand. |
| **R108** | `AMENDED-BY:R118` | *"DATED NOTE, 2026-08-06 (R118, §5 row 10.8) … Its 'released to the companion pool' justification … is **superseded by the cleaner principle**"* | Only the addendum's **justification**. *"The addendum above stands unchanged"* — Itto's registration is COMPANION CARD, Zhongli still holds slot 4. |
| **R116** | `AMENDED-BY:R117` | *"REQUIRED ANNOTATION, 2026-08-06 (R117, Q13). This ruling's stated consequence … is **overridden deliberately** by [USER]'s α selection"* | Only `NC-7`'s stated boss-room **consequence** (Kaiser Crab's second claw takes Vulnerable, not Frozen). Canonical Frozen and the other four canonicity rulings stand. |

Nothing else in any volume names an R-number in supersession language. The five
pre-derived rows already covered the ledger's only outright strikes.

## The 3 DOUBT rows — and why each refuses to resolve

| row | why it is arguable |
|---|---|
| **R59** — *Shop slot 2 floor: Uncommon* | R116's `NC-10` rules slot 2 **"any companion card" / unrestricted**, which is incompatible with R59's Uncommon-or-Rare floor — and R116 **names R59 in the same section** (*"`R59`'s slot-2 floor and `R60`'s override live in the same neighbourhood"*). But it names it as a **docket cross-note**, never as a strike. Cited-and-contradicted is not cited-as-superseded, and this pass will not upgrade one into the other. |
| **R103** — *the three probes, in cost order* | Supersession **by events rather than by text**. R103(b) gates the selector-recorded fanfare trace on P1.5 (*"It cannot run before the bridge records the Center Stage / Guest Cast choice"*), and R104 restates that gate as binding — yet R113 writes C2 off on a probe (b) whose own residual names *"the unrecorded Spotlight selector"* as term 1. Whether the gate was discharged, narrowed, or simply describes a different instrument than the probe that reported is a real question, and **no ruling names R103**. |
| **R107** — *the S4 hygiene report* | R118 §1 Q7 says *"the **R107/F1** fence re-points to the narrowed gate"* — naming the clause explicitly — while insisting *"the condition is the same condition, stated at the width that actually binds"* and *"Nothing is unfenced by this ruling"*. **Amendment of R107's F1 clause versus restatement of it at a narrower gate** is exactly the call this pass declines to make on its own authority. |

All three are one queue row (`docs/registry/user-queue.md` §4), **riding the
`S4-G9` sitting** per your order rather than standing alone.

## The 68 OPERATIVE rows — the blanket claim, stated so you can falsify it

Every one carries the same evidence string: **`no superseder cited (searched
DECISIONS*.md, klee-mod ledger, docs)`**. The search that backs it:

- every `tier0/DECISIONS*.md` volume (live + the R39–R99 archive) and
  `klee-mod/DECISIONS.md`, read entry by entry;
- a mechanical sweep of those volumes **and all of `docs/`** for
  supersede / amend / strike / discharge / withdraw / override / rescind /
  retract / obsolete language within three lines of any `R39`–`R120` token,
  plus targeted patterns for an R-number as the subject or object of such a
  verb.

**Four rows carry an extra note** rather than the bare string, because a reader
would otherwise expect a move: **R44** and **R99** each carry an R102 escrow
banner that R113 **struck** (*"the strike restores its pre-escrow status"*), so
both stand as ratified with R113 clause C-d's limits riding; **R52** is
**affirmed** by R118 §5 row 10.8 (*"R52 needs no amendment"*); **R60** is named
by R116's `NC-10` cross-note but nothing in that spec touches R60's content.

**The interpretive line this pass drew — the one thing worth overruling if you
disagree.** *A later balance dose on the same card or knob is not a superseder
of the ruling that shipped the earlier number.* R45's spender-Energy reprice does not
supersede R41's spend numbers; R110's `X3` (*"remove the energy rider and make
it free"*) does not supersede R42's Encore Performance refund; R49's
11-Block converter does not supersede R46's floor repair on the same card. Each
dose is a number in a declared sequence, taken in its own stamped world, and
every such ruling stands as the record of what it shipped. Reading it the other
way would have marked a large share of the balance ledger SUPERSEDED on
inference (share UNMEASURED — the point is that it is inference either way),
which is what the order forbids. The line is written into the sidecar's own header so it
can be overruled in one place.

## What is asked of you

1. **The objection window, open as of this page:** flag any row above and it
   reverts by handle `e0b563c`, no argument, no re-litigation. **Silence
   ratifies the batch.**
2. **One queue item:** the three DOUBT rows (R59, R103, R107), riding `S4-G9`.
3. **Nothing else.** No ruling text moved, no number moved, no gate opened or
   closed. The generated current-law digest in `tier0/DECISIONS.md` now states
   a status for every ruling instead of 77 shrugs.

**One thing the pass had to touch beyond paper, disclosed rather than buried.**
The digest generator's rendered header, and the test that guards it, both spoke
only of `UNREVIEWED`. With zero UNREVIEWED rows left, a test watching one value
would go quiet at exactly the point the file started making claims — so the
honesty clause is **generalized, not deleted**: every row must render as its
status, the header must count every category, and the UNREVIEWED half still
binds the moment a new ruling lands unread. Strictly stronger than what it
replaced.

*Verification: `lint_p_ledger` (*"8 row(s), all with five-line attestations; 8
handle commit(s) touch no [USER]-gated register"*), `lint_ledger_numbers`,
`lint_r_citations`, `lint_identifier_registry`, `gen_decisions_digest --check`
and the full suite green at the batch boundary.*

---

## RESOLUTION NOTE — 2026-08-06 (dispatch (e) / R121): the 3 DOUBT rows are answered

> **The tables above are NOT rewritten.** This page is the record of what the
> status pass found and what it refused to guess, and it stays exactly as
> delivered — including the "3 DOUBT" headline and the "why each refuses to
> resolve" table. This note is the answer arriving afterwards, appended.

[USER] resolved all three by name in the 2026-08-06(e) dispatch
(`docs/dispatch-2026-08-06e-six-replies.md`; ruling `tier0/DECISIONS.md`
**R121**). The verdicts, verbatim, with the scope each carries into
`tier0/decisions-status.tsv`:

| row | verdict | [USER], verbatim | scope recorded on the sidecar row |
|---|---|---|---|
| **R59** | `SUPERSEDED-BY:R116` | *"superceded but flag it for future design discussions (SHOULD it be rarity limited to avoid serving up crap cards, or is it fine to offer commons?) - this might need empirical data during a future round on the companion cards."* | **The slot-2 floor clause only.** R116's `NC-10` supersedes R59's Uncommon-or-Rare floor on slot 2; the rest of R59 is not named and is NOT judged. The flagged design question — *should slot 2 carry a rarity floor at all* — is minted on the `S4-G10`/`M11` shop close-out agenda, with the note that it wants empirical Common offer/pick/skip data from a future companion-card measurement round rather than an a priori ruling |
| **R103** | `OPERATIVE-NARROWED` | *"OPERATIVE-NARROWED."* | **R103(b)'s gate still binds any future selector-recorded fanfare trace**; the escrow strike stands unaffected (different question, different instrument). **No re-litigation of R113.** New status vocabulary, added by R121: an OPERATIVE row whose operating scope [USER] stated — still an absence claim, counted beside OPERATIVE and never among the moved rows |
| **R107** | `AMENDED-BY:R118` | *"AMENDED-BY:R118."* | **"Fence target only."** R90's banner and R118's re-point are formally reconciled as amendment, **zero behavioural difference**. R107's other findings are not named and are NOT judged |

**What this changes about the page above.** The headline's `DOUBT | 3` row is
now historical: as of this note the sidecar carries **zero** DOUBT rows. The
"one queue item" this page asked for — the three rows riding the `S4-G9`
sitting — is **CLOSED**, and `S4-G9`'s sitting shrinks by one. Nothing else on
this page moves: the 68 OPERATIVE rows, the 6 moved rows, the interpretive line
and the `e0b563c` revert handle all stand as delivered.

**Counts after the resolution** (mechanical, from the sidecar): **83 rows**
(R39–R121, R121 itself added by this dispatch) — **69 OPERATIVE**, **1
OPERATIVE-NARROWED**, **13 moved on an explicit citation**, **0 DOUBT**.
