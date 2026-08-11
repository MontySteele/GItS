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

> **Owner of every row below: [USER].** Status is OPEN unless a row says
> otherwise. Where a row needs a supporting evidence packet, it points to
> `→ review/active/<packet>`.

> The 2026-08-10 sitting ruled most of this register (R138–R174). Closed rows
> left HEAD; their rulings are in the commit messages of that date.

---

## 1. Furina — strength, legibility, and unshipped mechanics

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G7` | **RULED 2026-08-10 (R153): Furina gets three plans.** The remedy is one of two, and picking between them is what stays open: **rebalance the weak plans until they are viable**, or **expand salon to contain multiple archetypes**. The `R107`/`F1` fence dropped with `S4-G5`/`B-G1` (R138), so nothing gates this any more. **Choose a direction** against the options packet (BACKLOG `EB-81`). Standing read (`RT9/D14/P6/C8` · n=3000 · seed=20260729): salon **4.70%** [4.00, 5.52] / spotlight **1.50%** [1.12, 2.00] / fanfare **1.30%** [0.95, 1.77]; `real_silent` 1.37% [1.01, 1.85], `real_ironclad` 6.13% [5.33, 7.05]. Structure held — salon separates from both other plans, fanfare still overlaps the Silent floor, and salon now sits *below* `real_ironclad` | OPEN — direction pick, unfenced | user-queue §2; R107/F1; R153 → review/active/sitting-reads-2026-08-08.md §1 |
| `Q-C` (payoff-reach) | **Amended-rubric census in hand** (`114bed4`: unattributed 24 → 23, `Token:Shiv` admitted, the LOW floor moved). Remaining [USER] work, one commit: **ratify the amended rubric text** — including the Necrobinder third-spelling sub-question — then **commit the aims + the Q-A/Q-B direction-and-threshold predictions**, before any sprint number is read. Tentative aims recorded in packet §7.2 and NOT ratified: Klee D-MED / R-HIGH / S-LOW; Furina Sa-MED / Sp-HIGH / F-LOW; Kokomi P-MED / C-HIGH / A-LOW | OPEN — ratify, then predict | → review/active/payoff-census-2026-08-08.md §7; review/active/payoff-reach-reregistration.md §5; R137; R155 |

## 2. Kokomi — band, playtest, and levers

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | Declare Kokomi's HP stability band **from design intent, before her confirmatory playtest** (may not be revised against it). **RULED 2026-08-10 (R156): the declaration is deferred past the post-wave playtest, at [USER]'s pace** — a fresh volatility read is in hand (`a089fa2`, `review/active/volatility-read-2026-08-10.md`) and the declaration waits on the observation, not on more measurement. Finding worth carrying into the declaration: the **inversion** — Kokomi is worst on time-spent-low while Furina is the flattest | OPEN — declare, deferred to post-wave | user-queue §2; `DEC-D5` clauses 2–4; R156 |
| `S4-G13` | **RULED 2026-08-10 (R154): Kokomi needs a general power lift.** Suspected cause named in the ruling: assist's internal payoffs are missing — *"she really has two archetypes not three"*. **Build a legal lever-2 candidate (BACKLOG `EB-74`) and PULL NOTHING** until the post-wave observation lands. The open verb is **which lever to pull, and whether**, after that observation. Standing read (`RT9/D14/P6/C8` · n=3000 · seed=20260729): priest **1.10%** [0.78, 1.54] / commander **2.20%** [1.73, 2.79] / assist **0.57%** [0.35, 0.91] vs `real_ironclad` **6.13%** [5.33, 7.05] and `real_silent` 1.37% [1.01, 1.85] — all three below the Ironclad floor without interval overlap, assist below even the Silent floor | OPEN — pull-or-not, gated on the post-wave observation | user-queue §2; R154 → review/active/sitting-reads-2026-08-08.md §2 |
| `S4-G14` | Play the Kokomi protocol playtest deliberately against the written question list (exploratory runs cannot be graded). **Narrowed 2026-08-10 (R152):** `OT-1` is retired as a card question — *"Neap Tide"* is a **sprint name, not a card**, and `R115` reified it in error. The kit-level answer was given pre-wave and stands **provisionally**: kit fine-ish, concept works, not obviously weak, needs refinement — **no lever pulled on it**. What remains here is the **post-wave protocol run** | OPEN — table time; gated on `S4-G6` + the `EB-53` remnant | user-queue §2/§7; `docs/current/playtest/kokomi-playtest-protocol.md`; R115; R152 |

## 3. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M14` | **Countersign the shop-rerun pre-registration.** Drafted in the shop-floor worktree; it lands in HEAD with that branch — cite as incoming: `review/active/shop-rerun-registration-2026-08-10.md`. The rerun runs against the restored slot-2 Uncommon floor (`C9`, in-flight), so the registration must be countersigned before any number is read | OPEN — countersign; packet incoming with branch `shop-floor-2026-08-10` | 2026-08-10 sitting, `S4-G10` close-out (R149) |

## 4. Systems and data-model rulings

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M13` | `ROUTE_REGRET_MARGIN` and its twin — `draft_regret`'s `+ 1.0` at `tier05/draft.py:1694` — have no recorded derivation. **RULED 2026-08-10 (R164): pre-register the measurement; do NOT ratify `+1.0`.** A distribution printer is needed first (the pooled emitter emits no percentiles by design and the route-regret block is unprinted) — printer and registration draft are BACKLOG `EB-72`. The remaining [USER] verb is **countersign that pre-registration when it is drafted**. Until then only the margin-free reads (`mean/p50/p90/max_regret`) are quotable | OPEN — countersign pending the `EB-72` draft | EB-16w close-out 2026-08-07; `tier05/run_metrics.py` margin note; R164 |
| `M15` | **Ratify the rarity-comparability rule.** Card-sheet rarity sits **outside** the `RT/D/P/C` stamp, so a rarity edit moves the drafted world with **no version signal** — two worlds that differ only in a card's rarity are today indistinguishable to a reader of the stamp. Draft rule text for ratification: *"A card-sheet rarity change is a drafted-world change. It lands under a `CONSTANTS_VERSION` bump like any other balance constant, and numbers are not comparable across it."* **Ratify, amend, or reject.** Live occasion, now **landed and awaiting the rule that would have required it**: the `X7`+`X8` rarity erratum (R161/R162) joined `C9`'s open window on 2026-08-10 — batched under a single constants bump precisely because no rule says it must be, i.e. by house judgement rather than by law. Ratifying makes that the standing requirement; rejecting means the next rarity edit may legitimately ship with no stamp movement at all | OPEN — ratify | 2026-08-10 sitting (R161/R162 sequencing); minted 2026-08-10 |

## 5. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Read card names and lore text by eye before they ship** (R29d Furina pass; Kokomi's 20 authored-but-unaudited fill cards; kickoff ask 10) — ruled to have no substitute. **Grew 2026-08-10:** the `EB-22` fill names are **provisional pending this pass** (R157), and `EB-26`'s `D1` name eye-read joins the same pile (R158) | OPEN | user-queue §2; `tier0/DECISIONS.md` entry 75 + R29d; R157; R158 |
| `S4-G12` / `CC-G1` / `CC-G2` | Art contact-sheet eyes-on + in-game screenshot review of the twelve Curtain Call cards and the A0 smoke run. **Corrected 2026-08-10 (R166):** the re-hunt set is **FOUR**, not three — `warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`; `standing_room_only` is **overturned** and `grand_gala` is **displaced** from the set. The A0 elite smoke is **PARTIAL**. Materials are produced (`EB-54`); the eyes-on is still [USER]'s | OPEN — **materials ready** | user-queue §2; `review/active/art-runs-2026-08-08.md`; R166 |
| `S4-G17` | Three running-game looks (no full playtest): `AS2-D5` salon look and `AS2-B5` motion/facing taste (captures staged by BACKLOG `EB-52`); `AS2-E2` icon picks (canonical in the Art debt row below) | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2), §"Gates & rulings" |
| `M16` | `EB-53` capture `C7` — **re-spec the capture, or keep `SceneSlots` at 4 as headroom.** `C7` is unreachable as written: Sparks 'n' Splash is Klee-only and Bake-Kurage is Kokomi-only, so no creature can hold all four end-of-turn sources and the reachable maximum is three. **RULED 2026-08-10 (R170): deferred to observation** — the call is taken after the post-wave playtest, on how the docket reads in combat | OPEN — gated on the post-wave playtest | BACKLOG `EB-53` §7.4; minted 2026-08-10; R170 |
| S8 + S10 galleries | Taste calls on two proposal galleries: eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10 — RESKIN/REDESIGN is [USER]'s per north-star) | OPEN — taste | user-queue §4; `docs/current/dossiers/content/potion-relic-conversion-gallery.md`, `docs/current/dossiers/remap/reskin-gallery.md` |
| Art debt | **The art sitting's pick list, rewritten 2026-08-10 (R167 + R171).** **Adopted PROVISIONAL, pending eyes-on:** `standing_ovation`-ICON r2; `friendly_visit` "Gift" r2; `study_buddy` "Ragged Notebook" r2; `grand_gala` r6 (provisional — needs eyes); `ovation_trickle` r2, **superseded by the collision below**. **`EB-36` trio:** r2 across all three — they draw on different sources, so the distinct-crops instruction is inapplicable. **`curtain_cue`:** manual crop preferred over the staged candidates. **Power sigils:** the r2 batch stands **except** the `ovation_trickle` / `stagehands_encore` **collision** — the same source on two sigils; one of the two needs a different pick, and that pick is [USER]'s. **`ART-L12` card-face pair:** `crowd_work` == `standing_ovation` needs a `standing_ovation` **CARD** contact sheet before there is anything to pick from (production BACKLOG `EB-76`), then a pick. **`EB-39`** (`no_holding_back`): shortlist pick owed — r2 / r3 / r4 staged, r1 is the unchanged incumbent. **`spark_knight_style`** replacement pick, moved here from `S4-G20` (R146). **Still awaiting picks:** Kokomi 58 faces + 15 companions; `AS2-E2` icon picks. **Still awaiting images:** `breathless`, and the final crops. `EB-39` and the sigil collision are **art-review items, not word-now items** (R171) | OPEN — mostly taste | user-queue §8; `review/active/art-runs-2026-08-08.md`; `docs/current/art/kokomi-art-pass-requirements.md` §2a; R167; R171 |

## 6. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | **COUNTERSIGNED 2026-08-10 (R165)** — the C2 grading countersign is given. The sprint **closes only after [USER]'s later full card review**, which is what keeps this row open. Neuvillette **ships as-is** to unblock, and carries a redesign owed later. Still inside the row: the companion art picks (Navia / Clorinde / Neuvillette / Arlecchino) and the v1.7 lore/naming eyes-on audit, both non-delegable | OPEN — countersigned, closes on the full card review | user-queue §10; R165 |

## 7. Design calls raised by a graded measurement

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M17` | **`EB-17p` fired its redesign trigger on two cards — `borrowed_brilliance` and `elemental_ecstasy` — under §8.1's dead-in-hand clause. Redesign them, or accept them as they stand.** The sweep ran and was graded blind 2026-08-10 against predictions committed ahead of it (`eb67706`): **3 PREDICTED / 1 SPLIT / 1 MISS**, the miss being `borrowed_brilliance` on the **wrong sign**. `friendly_visit` came back PREDICTED-strong (+3.04 / +4.46). **Read §13.8's instrument caveat before designing against this:** un-upgraded `borrowed_brilliance` recorded **40,396 draws and 0 plays**, and that row cannot separate *pilot refusal* from *an unsatisfiable play condition* — a redesign argued from that row alone is arguing from an instrument reading, not from the card. The design act is the only thing left of the experiment; the measurement itself is complete | OPEN — design act | → review/active/eb17p-registration-draft-2026-08-08.md §13, §13.8; results `review/active/eb17p-results-2026-08-10.txt`; minted 2026-08-10 |

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
