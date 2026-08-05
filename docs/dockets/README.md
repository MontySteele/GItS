# Dockets — index

**Status:** INDEX. A docket is a holding place for items that have been
*routed* and not *decided*. Nothing in this directory carries design
authority, and nothing in it is scheduled work until the session it names
sits down.

Opened 2026-08-06 by the Second Wind batch (Track R), because the sitting of
2026-08-06 routed nine S13 families to four venues that did not exist as
documents. Rulings: `tier0/DECISIONS.md` R109, R110, R111.

| docket | what it holds |
|---|---|
| `klee-rework.md` | The Klee rework session's inbox: X1's note, X7's spark law plus the audit slot Track T fills, X8's rarity-check findings slot. |
| `kokomi-workshop.md` | The next Kokomi kit workshop's inbox: X9's charge-bank note. |
| `companion-pricing.md` | Companion pricing candidates. X10 lives here as a CANDIDATE — explicitly not ratified. |
| `watch-items.md` | The watch-item register: X4, X6, X12, each with the quantity watched and the trigger that brings it back. |

**House rules for this directory, so a docket cannot quietly become a plan.**

> **QUEUE POINTER, added 2026-08-06 by the housekeeping sweep (Track X).** The single source of truth for what is open and for whom is now **`docs/registry/user-queue.md`**. This section keeps its full text and stays the place the detail lives; the queue file is the index that says which items are still open, which were discharged and by which ruling. Where the two disagree about a *status*, the queue file is the later reconciliation. Identifier collisions (`G1`, `D5`, `C1`, `P1`, `S4`, `X<n>`) resolve at `docs/registry/identifiers.md`.


1. A docket entry records a verdict, a routing and a question. It does not
   record a proposal, a number or a fix.
2. Verbatim verdicts stay verbatim. Where a docket paraphrases, it says so.
3. HELD flags are copied in as held. Nothing may be built against a held flag
   — not a probe, not a pre-draft, not a "while we're in there".
4. An empty findings slot stays empty until the audit that fills it runs. An
   empty slot is information; a speculatively pre-filled one is not.
