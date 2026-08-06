# Dockets — index

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

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
| `engineering-backlog.md` | Open work that needs **no [USER] ruling to start**: confirmed defects, measurement defects, instruments that were directed and never built, content work with nothing in front of it. Opened 2026-08-06 by the docs diet (Track Z / Z-3) so that the three retired registers had somewhere to put their engineering half. |

**Where an open item may live.** As of 2026-08-06 there are exactly two homes:
`docs/registry/user-queue.md` for anything that needs [USER], and this
directory for anything routed and not decided.
`tools/lint_identifier_registry.py` RULE 3 fails a **new** document that mints
an open-item row anywhere else; the rule and its two escape hatches are
`docs/registry/identifiers.md` §16.

**House rules for this directory, so a docket cannot quietly become a plan.**

> **QUEUE POINTER** (Track X, 2026-08-06; compressed by Track Z, Z-6). Status for everything below lives in `docs/registry/user-queue.md`; short codes resolve at `docs/registry/identifiers.md`. Full rule: `docs/registry/identifiers.md` §16.


1. A docket entry records a verdict, a routing and a question. It does not
   record a proposal, a number or a fix.
2. Verbatim verdicts stay verbatim. Where a docket paraphrases, it says so.
3. HELD flags are copied in as held. Nothing may be built against a held flag
   — not a probe, not a pre-draft, not a "while we're in there".
4. An empty findings slot stays empty until the audit that fills it runs. An
   empty slot is information; a speculatively pre-filled one is not.
