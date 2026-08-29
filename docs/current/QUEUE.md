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
| `S4-G6` | **Ask:** declare Kokomi's HP stability band from design intent — never revisable against the playtest that grades it (D5). **Pick:** (1) Claude drafts the band DRAFTED from written design intent and you countersign in batch — **default** (R212(2)); (2) declare it at the table; (3) leave it DARK (`band = None`). **Gate:** the post-wave EXPLORATORY run comes first, the confirmatory protocol run after (R175) | OPEN — declare | user-queue §2; `DEC-D5` clauses 2–4; R156; R175; R212 |
| `S4-G14` | **Ask:** run the Kokomi confirmatory protocol and rule on its written question list — an exploratory run cannot be graded, and this one fills the Answers block. **Eyes-on:** `docs/current/playtest/kokomi-playtest-protocol.md`, question by question. **Gate:** the sequence R175 fixed — post-wave exploratory run → `S4-G6`'s band declaration → this run; plus `EB-53`'s remnant | OPEN — table time | user-queue §2/§7; R115; R152; R175 |

## 2. Shop, pricing, and money

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M14` | **Ask:** the companion channel's redesign trigger FIRED — re-price, re-stock, or leave it. **Pick:** (1) noise, close it — **default**: only condition 4 fired, mean Δ −0.07 pp, inside every interval; (2) reopen the design; (3) re-run at n = 2,000. **Context:** 28.6% of offers arrive unaffordable; relic buys run +1.7 pp in companion visits. **Gate:** none; measurement closed | OPEN — design call | R149; R182; graded 2026-08-26 → review/active/shop-rerun-registration-2026-08-10.md §8 |

## 3. Eyes-on reviews and taste

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G11` | **Ask:** read card names and lore by eye before shipping. **Eyes-on:** (a) *Backstroke* on `freminet_pressurized_floe`, not canon; (b) `EB-83`'s `tengu_flurry` / `chinowa_ward`; (c) the `EB-82` Grave labels. **Pick, (a):** (1) keep; (2) rename — canon is taken by `freminet_shattering_pressure`, and *Backstroke* is load-bearing in two sheets. **Gate:** R179 — prove neither id nor name is read | OPEN — eyes-on | user-queue §2; `tier0/DECISIONS.md` entry 75 + R29d; R157; R184 |
| `S4-G12` / `CC-G1` / `CC-G2` | **Ask:** approve or veto the twelve Curtain Call faces and the A0 smoke, by eye. **Eyes-on:** the `S4-G12` sheet, regenerated over all six gate rows. The re-hunt set is **FOUR** (`warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`) — `standing_room_only` overturned and `grand_gala` displaced (R166); the A0 smoke is PARTIAL. **Gate:** none; materials produced | OPEN — materials ready | user-queue §2; `review/active/art-runs-2026-08-08.md`; R166 |
| `S4-G17` | **Ask:** three running-game looks, no full playtest. **Eyes-on:** `AS2-D5` the salon; `AS2-B5` motion and facing taste; `AS2-E2` icon picks (canonical in the Art debt row). **Gate:** none — captures are staged and manifested | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2); `review/active/livegame-captures-2026-08-08.md` |
| `M16` | **Ask:** `EB-53` capture `C7` is unreachable as written — Sparks 'n' Splash is Klee-only and Bake-Kurage Kokomi-only, so no creature holds all four end-of-turn sources and the reachable maximum is three. **Pick:** (1) keep `SceneSlots` at 4 as headroom — **default**, the only non-arbitrary answer; (2) re-spec `C7` to the reachable three. **Gate:** the post-wave playtest (R170) | OPEN — the post-wave playtest | BACKLOG `EB-53`; minted 2026-08-10; R170 |
| `M26` | **Ask:** accept or amend the end-of-turn docket by eye (`EB-53` item 17a). **Eyes-on:** does the end of turn read legibly; is the per-seat position doing the attribution work; is the chip's prominence right. Frames in `art/eb52_captures/` and `understudy/logs/frames/`. **Caveat:** no frame isolates the electro (Oz) leg, so the pyro→electro ORDER falls to this look. **Gate:** none — 6 of 9 captures taken | OPEN — eyes-on | BACKLOG `EB-53` §7; live verification 2026-08-08 |
| `M19` | **Ask:** pick the five-layer Hydro orb art set for Furina's energy counter. **Pick:** (1) **A Fontaine Hydro** — **default**, closest to the base construction; (2) B Opera Pale (weakest darkened); (3) C Tidal (most legible). Sheet: `art/contact_sheet_eb88_energy_orb.html`. **Gate:** none — under R212(1) the default ships if no pick lands; veto on the sheet | OPEN — candidates ready | ex-`EB-40`; furina-art-pass-requirements §8; ungated 2026-08-13 (`EB-88`); R212 |
| S8 + S10 galleries | **Ask:** taste calls on two galleries — eight flagged potions/relics (S8), and enemies that could be reskinned rather than redesigned (S10). **Pick, per flagged body:** (1) RESKIN — **default** where the Genshin body is verified, five of six; (2) REDESIGN. Globe Head's silhouette is unresolved. **Gate:** none; both galleries are written | OPEN — taste | user-queue §4; `dossiers/content/potion-relic-conversion-gallery.md`; `dossiers/remap/reskin-gallery.md` |
| Art debt | **Ask:** three art picks a rank order cannot settle. Everything else ships under R212(1): rank 1 applied, veto on the sheet. **Pick:** (1) the `ovation_trickle`/`stagehands_encore` sigil COLLISION — move one off the shared source; (2) which Rare wears Kokomi's `Character Details 1` crop (L9's one exception); (3) `grand_gala` r6, provisional. **Gate:** none | OPEN — taste | user-queue §8; `review/active/art-runs-2026-08-08.md`; `art/kokomi-art-pass-requirements.md` §6; R167; R171 |

## 4. Fontaine Rares close-out

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M10` | **Ask:** approve the Fontaine Rares close — the full card review, with the v1.7 lore/naming audit riding on it. **Eyes-on:** the sprint's cards and the v1.7 lore/naming pass. Neuvillette **ships as-is** to unblock and carries a redesign later. **Gate:** none; the `C2` countersign was given (R165). The four companion art picks (Navia / Clorinde / Neuvillette / Arlecchino) now ship under R212(1), veto on the sheet | OPEN — closes on the full card review | user-queue §10; R165; R212 |

## 5. Post-playtest design calls

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M45` | **Ask:** ratify the pass's seven open calls as ONE slate (R206). **Pick (adopt / defer, audit first):** (1) `salon_rotate` reader / timing; (2) `smoke_and_sparks` re-body / cut; (3) `Win10`/`Win11` on choices / state; (4) Spotlight selector amend / accept; (5) `depths_judgment` flat-14 / rescale; (6) Kokomi Block cluster accept / amend; (7) Charge lever: `S4-G13`. **Gate:** the playtest | OPEN — after the playtest | R206; review/active/richness-playtest-brief-2026-08-26.md |

## 6. Build environment

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M46` | **Ask:** the machine's game left the pin — STS2 updated to **v0.111.0** on Steam's **`public-beta`**, and neither the vendored bridge nor `KleeCode` compiles against it. **Pick:** (1) opt back to `public`, pin unmoved; (2) port and re-pin (`EB-171`), which moves shipped C# behaviour; (3) keep a launchable 0.107.1 copy beside it. **Also:** `klee` is disabled in the game's own mod settings. **Gate:** none | OPEN — build-environment call | acceptance attempt 2026-08-28; `godot.log` |

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
