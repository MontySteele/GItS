# Surplus-dispatch-3 — curation touchpoints (charter §3.9)

One touchpoint per research stream, by the orchestrator (Fable), from each
stream's joined file and the agents' returned summaries. Curation SELECTS what
the morning reader opens first, DEDUPES claims that two streams both carry, and
ORDERS items — it never restates a claim more strongly than its file does and
never turns a candidate into a verdict. Where a stream's file says UNVERIFIED
or NON-FINDING, that is still the claim.

Format per stream: **Open first** (the one file / section to start from) ·
**Order** (what to read in what order, and why) · **Dedupe** (claims carried
elsewhere, and which file is the authority) · **Not for the sitting** (items
this curation routes away from the morning read, with the route).

---

## S15 — world-track sitting agenda  *(curated 2026-08-27 02:40)*

- **Open first:** `s15-world-sitting-agenda.md` §0 (dedupe log), then §A.
- **Order:** as the file lays it out — §A one-word calls (items 1–12) → §B
  short calls (13–47) → discussions. The agenda already dedupes against QUEUE,
  the 2026-08-08 sitting agenda and the current sitting reads; `M46` is absent
  in this checkout and the file says so.
- **Dedupe:** none against other streams — the galleries are this stream's
  only sources. Item 11 ("does the tier0 calibration battery stay unthemed")
  touches measurement law; it is an ask, not a finding, and stays where it is.
- **Not for the sitting:** the four hygiene findings near the end of the file
  (two stale line pointers boss gallery → enemy atlas; a file renamed without
  its citers updated; a cited path not in HEAD; one research correction nobody
  booked). These are dead-reference hygiene under `docs/current/dossiers/` —
  normal commits on a hygiene branch, NOT this dispatch branch (charter §2
  forbids `docs/current/` edits here). Routed to the orchestrator's morning
  hygiene list.

## S12 + S13 — public patterns and the engine socket probe  *(curated 2026-08-27 02:40)*

- **Open first:** `s12-public-patterns/s12-00-joined-read.md` §1 (the
  per-subsystem verdict table with one citation each), then
  `s13-engine-sockets.md` §3 (socket table keyed to S12a–g).
- **Order:** S12 §1 → S13 §3 → S13 §4.4–4.5 (which missing shapes fall back,
  and the authoring escape hatch BaseLib already ships) → S13 §5 (the open
  socket questions S1–S3, which are also lane D's go/no-go residue) → S12 §3
  transfer questions. Within S12 §3, read group **A (dependency pin)** first:
  our manifest pins BaseLib ≥ 3.3.6, the monster/encounter API is read at
  3.4.5, and S20's packaging census reports the same three-number skew
  independently — it gates every other transfer question. Then F
  (registration route), C (save / identity / removal), then the rest.
- **Dedupe:** four claims appear in BOTH S12 §2.3 and S13 §5 — no `BossModel`
  (a boss is `EncounterModel` + `RoomType.Boss`); no declarative data format
  for enemies/encounters/acts/events; `MegaCrit.Sts2.Core.Hooks` is a
  combat/run callback bus, not a world-event system; the class name is the
  save id (`Slugify(type.Name)`). **S13 is the authority** (engine decompile);
  S12 corroborates from mod source. S12 §2.1 records its own internal
  reconciliations (BaseLib licence, the 24-vs-shipped Downfall model count,
  the pin confidence levels) — read as resolved there, not re-opened.
- **Not for the sitting:** S12's search-boundary blockers (GitHub REST rate
  limit; code search behind auth) are runner facts for BLOCKERS.md, not
  decisions. S13's "which enemy is the right subject" (its §5 #5, Nibbit) and
  S16's Mawler pick are two PROPOSED picks for the same slot — flagged for
  the lane D / S16 line of the morning read, not resolved here.

## S18 — enemy feasibility  *(curated 2026-08-27 02:40)*

- **Open first:** `s18-enemy-feasibility/s18-joined-matrix.md` §1 (socket
  resolution after S13) and §3a (complexity across the mapped set).
- **Order:** §1 → §3a → §3c (**the boss surcharge is invisible in the
  complexity letter** — the one methodological caveat to hold while reading
  any row) → §5 questions. Within §5, questions 1–4 are SCOPE (unmapped
  Overgrowth encounters, Act 1 research bosses, the Underdocks block, the
  five-body leftovers row) and come before 5–12, which presuppose a scope.
- **Dedupe:** §1's two socket facts (a non-Spine body is a supported state end
  to end; there is no public API to replace a base monster's art — the seam is
  a Harmony patch) restate S13 §4.4 and §5.1 #4 — that is the join working as
  designed; S13 remains the citation. `s18-bosses-elites.md` §3d reconciles the
  three act files against each other; the matrix carries the reconciled rows.
- **Not for the sitting:** the per-act files' three process blockers (scratch
  directory collision between the Act-1 and Act-2 agents; the broken `python`
  alias; one PowerShell extraction timeout) — runner facts for BLOCKERS.md.
  Nothing in S18 is a mapping verdict, and this curation keeps it that way.

## S14 — Elemental Resonance pre-read (SURPLUS)  *(curated 2026-08-27 02:40)*

- **Open first:** `s14-resonance-preread.md` §1.4 — the source disagreement
  found tonight (official page behind the community wiki on wording; a
  widely-mirrored third-party summary contradicting both). Read it before
  citing any number from §1.2.
- **Order:** §1.4 → §1.2 (the composition table, official wording) → §2.2
  (fixed vs dynamic payoff layer) → §3.1 (NON-FINDING: no composition passive
  in Downfall) → §4 (questions only). Read last in the morning, per the
  charter.
- **Dedupe:** none; nothing else in the dispatch touches Resonance.
- **Not for the sitting:** all of it — the charter keeps this stream
  surplus-only and non-critical-path. No item is promoted into the sitting
  by this curation. §4 was checked for declarative design: it is questions.

---

## Pending curation (resumed agents still running as of 02:40)

- **S16** — the joined capability matrix is being rewritten by the resumed
  agent (the first write landed on disk before its return failed).
- **S17** — the companions family and the joined ledger + batches.
- **S19** — the whole stream.
- **S20** — the save/update/removal family and the joined matrix.

Tooling lanes A–D are branch handoffs, not research streams, and are not
curated: their handoff notes are read as written in the morning-read order
(`tooling-lane{a,b,c,d}-handoff.md` on each lane's own branch).
