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

## S16 — native-animation grammar and corpus  *(curated 2026-08-27 10:40)*

- **Provenance caveat first:** `s16-animation/s16-joined-capability-matrix.md`
  was written by its agent at 00:41; that agent's return then failed on the
  usage limit, and the resumed rewrite was throttled for eight hours without
  finishing and was stopped. The file on disk is complete and internally
  consistent but **its author never confirmed it**. Read it as the join it
  is; where it and a body file disagree, the body file is the source.
- **Open first:** the matrix §0.2 ("the rows are not mutually exclusive, and
  that is the first finding") and §1 (the joined matrix).
- **Order:** §0.3 (what the integrator verified first-hand) → §1 → §3.1 (the
  failure ladder, corrected, with one conflict between corpus files
  RESOLVED) → §3.2 (what Spine gives free — the five-item price list every
  other approach must pay) → §3.3 (the trigger seam: three shapes, one naming
  skew, one takeover) → §3.4 (combat is paced by C# constants, not clip
  length) → the per-approach detail in §2 only as needed. The four body picks
  (Ironclad / Regent / Mawler / Ceremonial Beast) are PROPOSED technical
  picks in `s16-00-schema.md`, with rejected alternatives recorded there.
- **Dedupe:** lane A's bake-off measures the same four approaches on a
  synthetic rig; the matrix is the base-game evidence and lane A is the
  mod-side measurement — read them together, cite each to its own file.
  Three distinct latent defects for spine-less visuals are carried by three
  files and are NOT one finding: `NCreature::StartDeathAnim` gating death
  SFX/length (`s16-00-schema.md`), `ImmediatelySetIdle` bypassing our patched
  trigger and `StartReviveAnim` gating on `_spineAnimator` (lane A's
  handoff). S13 §5 #5 (Nibbit) and S16's Mawler are two PROPOSED picks for
  the same "ordinary enemy" subject — flagged, not resolved.
- **Not for the sitting:** every capture slot is "capture pending" (no game
  launch was permitted); Spine clip durations and bone/slot counts need a
  `.skel` parser nobody wrote — runner facts for BLOCKERS.md.

## S17 — art coverage, provenance, batch plan  *(curated 2026-08-27 10:40)*

- **Open first:** `s17-art/baseline-run-2026-08-26.txt` for the numbers
  (270 covered / 24 missing card-sized; the charter's 39/255 was stale), then
  `s17-icons-ui-models-vfx.md` §1 — the one-paragraph shape of everything
  that is NOT a card, which is the cross-family view the deferred ledger
  would have given.
- **Order:** icons/UI §2d (seven powers with **no icon mapping at all** —
  reported, not filed) → `s17-furina.md` §4b (the seven absent sigils,
  `EB-65`) and §6a (`M19`, cited not picked) → `s17-kokomi.md` §4 (**22 Kokomi
  asset ids have no `SOURCES.tsv` row at any rank** — the provenance gap) →
  `s17-klee.md` §1.1 (the provenance hole, stated precisely) → the collision
  sections (klee §3.1, furina §8, kokomi §5b).
- **Dedupe:** the seven unmapped powers are the same list the EB-67 artifact
  reported — one item. The 25-of-27 dead contact sheets are reported by three
  family files — BLOCKERS.md carries it once. `s17-furina.md` says `EB-65`
  "cannot close mechanically: no rank-1 row exists" while BACKLOG's `EB-65`
  row says "the art exists — apply rank 1": the file's reading is the
  more specific one; the row needs a hygiene correction AFTER [USER] reads
  the sheet question (routed to the morning hygiene list, not changed here).
- **Deferred:** the companions family and the joined ledger + batches. Lane
  B's machine-readable ledger (branch `dispatch3-laneB-art-ledger`) is the
  tooling counterpart and stands on its own.
- **Not for the sitting:** rights tiers are categories only in every file —
  no verdict is implied by their counts.

## S20 — release, accessibility, localization census  *(curated 2026-08-27 10:40)*

- **Open first:** `s20-packaging-metadata-credits.md` "Overview — the six
  things worth knowing", then `s20-player-count.md` §2 ("the one asymmetry
  worth [USER]'s eye").
- **Order:** packaging **P1** (`0.2-1159` is not semver — amends LAW R70, a
  pick) → **P8** (the package is entirely Tier F art — the gating rights
  call) → **P6** (the BaseLib pin joins nothing) →
  `s20-performance-size-load.md` (79 MiB package; RGBA-for-nothing; format is
  a pick) → player-count §2 (LAW R144 promises multiplayer-only cards, we
  ship zero) and §3 (team-wide reaction counters in a per-seat row) → the
  three inventories (controller/resolution/text, color/effect/reduced-motion,
  localization seams), whose UNKNOWN rows are honest and mostly "needs the
  game".
- **Dedupe:** the BaseLib pin skew appears in S12 §3.A, S12b and S20 P6 —
  one item, S20 P6 has the three numbers. "Needs the game" rows across S20
  and S16's capture slots are one runner fact.
- **Deferred:** the save/update/removal family and the joined matrix.
- **Not for the sitting:** P9 (CI packages nothing — works as specified),
  P11 (UTF-8 BOM tolerated — NON-FINDING, verified), P12 (old handoff zips —
  informational).

## S19 — audio/VFX  *(DEFERRED — nothing to curate)*

The stream produced no file. When it re-runs, three pointers already exist
for it: S13 §5's socket question S3 (can a mod supply the FMOD events the
id-derived SFX paths demand out of `res://banks/desktop/*.bank`); the
death-SFX gating in `s16-00-schema.md`; and lane A's VFX/audio-hook column
on the synthetic rig.

---

Tooling lanes A–D are branch handoffs, not research streams, and are not
curated: their handoff notes are read as written in the morning-read order
(`tooling-lane{a,b,c,d}-handoff.md` on each lane's own branch).
