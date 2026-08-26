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

> **Every row is an ASK, a numbered PICK list with a marked default where one
> is defensible, and a GATE (R212).** A question that returns to [USER] never
> returns as a blank. Where the judgment is a look rather than a choice, the
> row prints **Eyes-on:** what to look at, in place of the pick list. How a
> row reached its current state lives in the commit messages that carry it
> (CLAUDE.md §Norms).

> **Owner of every row below: [USER].** Status is OPEN unless a row says
> otherwise. Where a row needs a supporting evidence packet, it points to
> `→ review/active/<packet>`.

---

## 1. Kokomi — band, playtest, and levers

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | **Ask:** declare Kokomi's HP stability band from design intent — never revisable against the playtest that grades it (D5). **Pick:** (1) Claude drafts the band DRAFTED from written design intent and you countersign in batch — **default** (R212(2)); (2) declare it at the table; (3) leave it DARK (`band = None`). **Gate:** the post-wave EXPLORATORY run comes first, the confirmatory protocol run after (R175). Finding to carry in: Kokomi is worst on time-spent-low, Furina flattest | OPEN — declare | user-queue §2; `DEC-D5` clauses 2–4; R156; R175; R212 |
| `S4-G13` | **Ask:** pull the staged Kokomi lever, or hold it. **Pick:** (1) hold until the playtest — **default**, both audits say freeze and play; (2) pull `staged/eb74-lever2-b-alone` (`CHARGE_PER_EXHAUST` 1→2); merging it IS the pull, and it re-baselines on whatever is live. **R205:** pull only if the table read says Kokomi is *generally underpowered*, **not merely that assist is inaccessible** — access repairs go through `EB-118` Phase 3 (R199). **Gate:** the post-wave observation | OPEN — pull or hold | user-queue §2; R154; R190; R205; BACKLOG `EB-74` → review/active/eb74-lever2-options-2026-08-13.md |
| `S4-G14` | **Ask:** play the Kokomi confirmatory protocol run deliberately against the written question list — an exploratory run cannot be graded, and this one fills the Answers block. **Eyes-on:** `docs/current/playtest/kokomi-playtest-protocol.md`, question by question. **Gate:** the sequence R175 fixed — post-wave exploratory run → `S4-G6`'s band declaration → this run; plus `EB-53`'s remnant. `OT-1` is retired (R152): *Neap Tide* is a sprint name, not a card | OPEN — table time | user-queue §2/§7; R115; R152; R175 |

## 2. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M14` | **Ask:** the companion channel's redesign trigger FIRED — re-price, re-stock, or leave it. **Pick:** (1) noise, close it — **default**: condition 4 alone fired, at mean Δ **−0.07 pp**, inside every interval; signs disagree by character; (2) reopen the design; (3) re-run at n = 2,000. **Context, never voted with:** 28.6% of offers arrive unaffordable (0–5% entered); relic buys run **+1.7 pp** in companion visits (−15 pp entered). **Gate:** none, the measurement is closed | OPEN — design call | 2026-08-10 sitting (R149); R182; run + blind grade 2026-08-26 (2 PREDICTED / 1 SPLIT / 2 MISS) → review/active/shop-rerun-registration-2026-08-10.md §8; raw review/active/shop-rerun-results-2026-08-26.txt |

## 3. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Ask:** read card names and lore by eye before they ship. **Eyes-on:** (a) `freminet_pressurized_floe`'s *Backstroke* is not canon; (b) `EB-83`'s provisional `tengu_flurry` / `chinowa_ward`; (c) the `EB-82` Grave of the Forgotten labels. **Pick, (a):** (1) keep it; (2) rename — canon is taken by `freminet_shattering_pressure`, and *Backstroke* is a pricing precedent at `furina-upgrades.yaml:205` that moves with it. **Gate:** R179 — prove neither id nor name is read mechanically | OPEN — eyes-on | user-queue §2; `tier0/DECISIONS.md` entry 75 + R29d; R157; R179; R184 |
| `S4-G12` / `CC-G1` / `CC-G2` | **Ask:** the art contact-sheet eyes-on plus the in-game screenshot review of the twelve Curtain Call cards and the A0 smoke run. **Eyes-on:** the `S4-G12` sheet, regenerated over all six gate rows. The re-hunt set is **FOUR** (`warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`) — `standing_room_only` overturned and `grand_gala` displaced (R166); the A0 elite smoke is PARTIAL. **Gate:** none — materials are produced | OPEN — materials ready | user-queue §2; `review/active/art-runs-2026-08-08.md`; R166 |
| `S4-G17` | **Ask:** three running-game looks, no full playtest. **Eyes-on:** `AS2-D5` the salon; `AS2-B5` motion and facing taste; `AS2-E2` icon picks (canonical in the Art debt row). **Gate:** none — captures are staged and manifested | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2); `review/active/livegame-captures-2026-08-08.md` |
| `M16` | **Ask:** `EB-53` capture `C7` is unreachable as written — Sparks 'n' Splash is Klee-only and Bake-Kurage Kokomi-only, so no creature holds all four end-of-turn sources and the reachable maximum is three. **Pick:** (1) keep `SceneSlots` at 4 as headroom — **default**, the only non-arbitrary answer; (2) re-spec `C7` to the reachable three. **Gate:** the post-wave playtest (R170) — the call is taken on how the docket reads in combat | OPEN | BACKLOG `EB-53`; minted 2026-08-10; R170 |
| `M26` | **Ask:** whether the end-of-turn attribution docket READS right (`EB-53` item 17a). **Eyes-on:** does the end of turn become legible; is the per-seat position doing the attribution work; is the chip's prominence right against the creature it sits under. Frames in `art/eb52_captures/` and `understudy/logs/frames/`. **Caveat:** no frame isolates the electro (Oz) leg, so the printed pyro→electro ORDER falls to this look. **Gate:** none — 6 of 9 captures taken, machine checks passed | OPEN — eyes-on | BACKLOG `EB-53` §7; live verification 2026-08-08; minted 2026-08-12 |
| `M19` | **Ask:** pick the five-layer Hydro orb art set for Furina's energy counter. **Pick:** (1) **A Fontaine Hydro** — **default**, closest to the base game's own construction; (2) B Opera Pale, the weakest when darkened, which the sheet shows; (3) C Tidal, most legible and furthest from the base colour language. Sheet: `art/contact_sheet_eb88_energy_orb.html`. **Gate:** none — under R212(1) the default ships if no pick lands and the veto is on the committed sheet. | OPEN — candidates ready | ex-`EB-40`; furina-art-pass-requirements §8; ungated 2026-08-13 (`EB-88`); R212 |
| S8 + S10 galleries | **Ask:** taste calls on two galleries — eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10). **Pick, per flagged body:** (1) RESKIN — **default** where the Genshin body is verified, five of six (Prism Slime, Churldric, Mystifying Megachurl, Polychrome Tri-Stars, Oprichniki); (2) REDESIGN. *Nod-Krai Scavengers* is an unnamed grouping and carries no row; Globe Head's silhouette is unresolved. **Gate:** none; both galleries are written | OPEN — taste | user-queue §4; `docs/current/dossiers/content/potion-relic-conversion-gallery.md`; `docs/current/dossiers/remap/reskin-gallery.md` |
| Art debt | **Ask:** three art picks a rank order cannot settle. Everything else in the pass ships under **R212(1)** — Claude applies rank 1, [USER] vetoes on the committed sheet. **Pick:** (1) the `ovation_trickle` / `stagehands_encore` sigil COLLISION — move (a) one or (b) the other off the shared source; (2) which Rare wears Kokomi's `Character Details 1` crop, the L9 ban's one approved exception; (3) `grand_gala` r6, adopted provisional and owed eyes. **Gate:** none | OPEN — taste | user-queue §8; `review/active/art-runs-2026-08-08.md`; `docs/current/art/kokomi-art-pass-requirements.md` §6; R167; R171; R212 |

## 4. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | **Ask:** the Fontaine Rares sprint closes on the full card review; the lore/naming audit rides with it. **Eyes-on:** the sprint's cards and the v1.7 lore/naming pass. Neuvillette **ships as-is** to unblock and carries a redesign owed later. **Gate:** none; the `C2` countersign was given (R165). The four companion art picks (Navia / Clorinde / Neuvillette / Arlecchino) have LEFT this row: under R212(1) they ship on rank 1 with veto on the committed sheet | OPEN — closes on the full card review | user-queue §10; R165; R212 |

## 5. Post-playtest design calls

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M45` | **Ask:** the richness pass's seven calls, ONE slate (R206), after the playtest. **Pick, adopt / defer (audit pick first):** (1) `salon_rotate`: reader / timing; (2) `smoke_and_sparks`: re-body / cut; (3) `Win10`/`Win11` scored on choices / state; (4) Spotlight selector: amend / accept; (5) `depths_judgment`: keep flat-14 / restore scaling; (6) Kokomi's flat-Block cluster + duplicates: accept / amend; (7) the Charge lever stays `S4-G13`. **Gate:** the playtest | OPEN — after the playtest | four internal reviews + external GPT audit 2026-08-26; [USER] remark 2026-08-26 (item 4) → review/active/richness-playtest-brief-2026-08-26.md; standing read review/active/sitting-reads-2026-08-25-c19-d17-p10.md §§1–2; cross-ref `S4-G13`; minted 2026-08-26 |

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
