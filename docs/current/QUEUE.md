# QUEUE

> This file holds **only OPEN decisions that need [USER]
> judgment** — design, behavior, taste, or money calls. It is one of six
> governing files and owns no overlap: executable engineering work lives in
> **BACKLOG.md**, settled normative rules in **LAW.md**, shipped facts in
> **STATE.md**. Nothing here is decided; recording is not answering.
> **Admission test (R136):** every row must contain an explicit human-only
> verb — *choose, ratify, amend, accept taste, or approve spend*. Work that
> reads, captures, schedules, audits, drafts, measures, or investigates
> defaults to BACKLOG or a review packet: it may *feed* a row, never *be*
> one. Identifiers are preserved from their source registers; new rows mint
> fresh ids.
> **Row shape (R177):** a row is **the decision, the choices, the gate, and
> at most one evidence pointer**, quoting at most one headline number or
> finding. Chronology, measurements, and case history live in the pointed
> packet or in the ruling's commit message — never in the cell. The commit
> that trims or closes a row preserves the old prose in history by
> construction.

> **Owner of every row below: [USER].** Status is OPEN unless a row says
> otherwise. Where a row needs a supporting evidence packet, it points to
> `→ review/active/<packet>`.

> The 2026-08-10 sitting ruled most of this register (R138–R174). Closed rows
> left HEAD; their rulings are in the commit messages of that date.

---

## 1. Furina — strength, legibility, and unshipped mechanics

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G7` | **Choose Furina's remedy direction (R153: she gets three plans):** rebalance the weak plans until viable, or expand salon to contain multiple archetypes. Unfenced — the `R107`/`F1` fence dropped with R138. Headline standing read: salon separates from both other plans and still sits below the `real_ironclad` floor. Decision packet: BACKLOG `EB-81` | OPEN — direction pick | R107/F1; R153 → review/active/sitting-reads-2026-08-08.md §1 |
| `Q-C` (payoff-reach) | **Ratify the amended rubric text** (including the Necrobinder third-spelling sub-question), then **commit the aims + the Q-A/Q-B direction-and-threshold predictions** — in that order, before any sprint number is read. Tentative aims sit in packet §7.2, NOT ratified | OPEN — ratify, then predict | R137; R155 → review/active/payoff-census-2026-08-08.md §7 |

## 2. Kokomi — band, playtest, and levers

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | **Declare Kokomi's HP stability band from design intent**, before her confirmatory playtest (may not be revised against it). Deferred past the post-wave **exploratory** run (R156; R175 — the confirmatory `DEC-D5` run follows the declaration). Finding to carry in: the inversion — Kokomi is worst on time-spent-low while Furina is the flattest | OPEN — declare, after the post-wave exploratory run | `DEC-D5` clauses 2–4; R156; R175 → review/active/volatility-read-2026-08-10.md |
| `S4-G13` | **Which lever to pull on Kokomi's general power lift, and whether** — after the post-wave observation (R154: a lift is needed; suspected cause, assist's missing internal payoffs — *"she really has two archetypes not three"*). The candidate is built by BACKLOG `EB-74` and **nothing is pulled** until the observation lands. Headline read: all three plans sit below the Ironclad floor without interval overlap; assist below even the Silent floor | OPEN — pull-or-not, gated on the post-wave observation | R154 → review/active/sitting-reads-2026-08-08.md §2 |
| `S4-G14` | **Play the Kokomi confirmatory protocol run deliberately against the written question list** (exploratory runs cannot be graded). Sequence (R175): post-wave exploratory run → `S4-G6` band declaration → this run. `OT-1` is retired (R152 — *"Neap Tide"* is a sprint name, not a card; the kit-level answer stands provisionally, no lever pulled) | OPEN — table time; gated on the `EB-53` remnant | R115; R152; R175 → `docs/current/playtest/kokomi-playtest-protocol.md` |

## 3. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M14` | **Fill the six `§5` prediction slots in the shop-rerun pre-registration, then countersign it — in that order, before any seed is run.** Re-stamped to `RT10/D14/P7/C9` (R176): `P7` moves every Klee tier0.5 number and Klee is one of the cell's three characters, so the Q1–Q4 predictions are authored against the P7 baseline | OPEN — fill `§5`, then countersign | R149; R176 → review/active/shop-rerun-registration-2026-08-10.md |

## 4. Systems and data-model rulings

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M13` | **Countersign the `ROUTE_REGRET_MARGIN` / `draft_regret +1.0` pre-registration when BACKLOG `EB-72` drafts it** (R164: pre-register the measurement; do NOT ratify `+1.0`). Until then only the margin-free reads are quotable | OPEN — countersign pending the `EB-72` draft | EB-16w close-out 2026-08-07; R164 |
| `M15` | **Ratify the card-sheet comparability rule.** The card sheets sit outside the `RT/D/P/C` stamp, so a sheet edit can move the drafted or combat world with no version signal. PROPOSED text: *"A card-sheet edit that materially changes the drafted or combat world — card additions or removals, cost changes, effect-number changes, rarity moves — is a world change. It lands under a `CONSTANTS_VERSION` bump like any other balance constant, and numbers are not comparable across it."* Two live demonstrations: the `X7`/`X8` erratum joined `C9` by house judgement rather than by law (R161/R162), and `EB-26` added a draftable card with no stamp movement at all. **Ratify, amend, or reject** | OPEN — ratify (PROPOSED text) | minted 2026-08-10; broadened 2026-08-11 |

## 5. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Read card names and lore text by eye before they ship** — ruled to have no substitute. The pile: the R29d Furina pass; Kokomi's 20 authored-but-unaudited fill cards; the `EB-22` fill names, provisional pending this pass (R157); `EB-26`'s `D1` name (R158) | OPEN | `tier0/DECISIONS.md` entry 75 + R29d; R157; R158 |
| `S4-G12` / `CC-G1` / `CC-G2` | **Art contact-sheet eyes-on + in-game screenshot review** of the twelve Curtain Call cards and the A0 smoke run (PARTIAL). The re-hunt set is FOUR (R166): `warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`. One line still owed here: *which three* the row names was never written down | OPEN — materials ready | R166 → review/active/art-runs-2026-08-08.md |
| `S4-G17` | Three running-game looks (no full playtest): `AS2-D5` salon look and `AS2-B5` motion/facing taste (captures staged by BACKLOG `EB-52`); `AS2-E2` icon picks (canonical in the Art debt row below) | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | `docs/animation-sprint-2-plan.md` (B5/D5/E2) |
| `M16` | **Re-spec `EB-53` capture `C7`, or keep `SceneSlots` at 4 as headroom** — `C7` is unreachable as written (no creature can hold all four end-of-turn sources; the reachable maximum is three). Deferred to observation (R170): taken after the post-wave playtest, on how the docket reads in combat | OPEN — gated on the post-wave playtest | BACKLOG `EB-53`; R170 |
| `M19` | **Approve or choose the five-layer Hydro orb art set** for Furina's energy counter scene. No precedent exists — all three characters return the base game's counter, and the base scene wants five orb-layer textures, so a Furina counter needs the Hydro set before the scene can be authored. Icons shipped 2026-08-08; this is the layer set, an art call. Engineering half: BACKLOG `EB-40`, gated on this pick | OPEN — art call | furina-art-pass-requirements §8; split 2026-08-11 |
| S8 + S10 galleries | Taste calls on two proposal galleries: eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10 — RESKIN/REDESIGN is [USER]'s per north-star) | OPEN — taste | `docs/current/dossiers/content/potion-relic-conversion-gallery.md`; `docs/current/dossiers/remap/reskin-gallery.md` |
| Art debt | **The art sitting's pick list (R167 + R171).** Picks owed: the `ovation_trickle` / `stagehands_encore` **sigil collision** (same source on two sigils — one needs a different pick); the `ART-L12` card-face pair `crowd_work` == `standing_ovation` (needs the `EB-76` sheet first, then a pick); **`EB-39`** `no_holding_back` shortlist (r1–r4 staged; if all four are rejected the honest next move is a manual crop or Tier O — no large landscape blast exists in the free Klee pool); `spark_knight_style` replacement (R146); Kokomi 58 faces + 15 companions; `AS2-E2` icons. **Adopted PROVISIONAL pending eyes-on:** `standing_ovation`-ICON r2; `friendly_visit` r2; `study_buddy` r2; `grand_gala` r6; `ovation_trickle` r2 (superseded by the collision); the `EB-36` trio r2; `curtain_cue` manual crop; the power-sigil r2 batch except the collision. **Still awaiting images:** `breathless`, final crops. `EB-39` and the collision are art-review items, not word-now (R171). Candidate detail: the packet's 2026-08-11 addendum | OPEN — mostly taste | R167; R171 → review/active/art-runs-2026-08-08.md §A |

## 6. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | **COUNTERSIGNED 2026-08-10 (R165)** — the C2 grading countersign is given; Neuvillette ships as-is and carries a redesign owed later. The sprint **closes only after [USER]'s later full card review**, which is what keeps this row open. Still inside: the companion art picks (Navia / Clorinde / Neuvillette / Arlecchino) and the v1.7 lore/naming eyes-on audit, both non-delegable | OPEN — countersigned, closes on the full card review | user-queue §10; R165 |

## 7. Design calls raised by a graded measurement

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M17` | **`EB-17p`'s redesign trigger fired on `borrowed_brilliance` and `elemental_ecstasy` (§8.1 dead-in-hand): redesign them, or accept them as they stand.** Graded blind 2026-08-10: 3 PREDICTED / 1 SPLIT / 1 MISS (`borrowed_brilliance`, wrong sign). §13.8's instrument caveat is RESOLVED (R176): the 40,396-draws / 0-plays row was pilot refusal, and under `P7` the base card plays ~6.1% — **design against P7 behaviour, not the pre-P7 row.** Two faithful routes: the design act now, or defer it behind a re-registered `P7` re-measure of the five-card sweep; an unregistered re-grade of the frozen §13 is not one | OPEN — design act | minted 2026-08-10; R176 → review/active/eb17p-registration-draft-2026-08-08.md §13 |

---

## Not carried here

Engineering follow-through lives in **BACKLOG.md**; the rules these decisions
settle in **LAW.md**. Closed and answered items leave HEAD — they are in git
history at tag `pre-simplification-2026-08-06`, and rulings from 2026-08-10
onward are in that date's commit messages.

Provenance entries are frozen citations: identifiers (`user-queue §2`,
`eng-backlog`, `dockets/…`, the DECISIONS ledgers) and any path not in HEAD
(`docs/archive/…`, `docs/registry/…`, retired sprint plans) name their
source as it stood when the row migrated. Retrieve any of them with
`git show pre-simplification-2026-08-06:<path>`.

A citation written as a whole `git show <commit>:<path>` command is one whose
content differs from the tag copy, so the commit — not the tag — is the
retrieval point. On a shallow clone, fetch it first:
`git fetch --depth=1 origin <commit>`. If a named commit is unreachable from
`origin` (it was only ever on a merged branch), it may still be present in the
local object store — try `git show <commit>:<path>` before concluding the
citation is dead.
