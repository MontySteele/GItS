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

## 6. Prototype slices (R213) — held arms, re-authored kits, and the rules under them

Each row points at the packet section that carries the options in full; the
packet is the argument and this is the register.

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M47` | **Ask:** choose what happens to *Bag of Tricks*, the arm the doctrine gate held on a top-level-cost clause and a D4 defect. **Pick:** (1) drop it; (2) amend the top-level-cost rule to admit a mode price; (3) build per-mode playability (`EB-182`) first, then re-ask — my reading; (4) re-author as two cards; (5) price the whole card. In full: §6.1 | OPEN — design call; nothing is gated on it | review/active/klee-slice-1-2026-08-29.md §6.1; R213 E2 |
| `M49` | **Ask:** close or keep the pilot's Charge hold-versus-spend term, moot under the Kurage-memory design — each memory carries its own price, so nothing is held. **Pick:** (1) close it, defer a *tempo* term to the re-authoring — **default**, `POLICY_VERSION` stays frozen; (2) build it anyway, version bump and re-baseline. **Gate:** none | OPEN — superseded, needs closing | kurage-memory packet §4, §9; R219 D |
| `M50` | **Ask:** rule on the four rows the Kurage-memory redesign leaves unruled — its five accrual options are WITHDRAWN (R219 D). **Pick, one each:** (1) *Bake-Kurage* the card, now unreachable; (2) its upgrade delta; (3) the Casket refresh link, now silent — answered by `M60` `KO2`; (4) `KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON`. Options per row: §12.4 | HELD — decides the shipped kit | kurage-memory packet §12.4, §11.6; R219 D; R220 B |
| `M52` | **Ask:** countersign the Furina reframe — the Salon is an orb board, Fanfare is its Focus and its Burst, Encore aims it (R220 A). **Pick:** (1) the packet's §3 ruling text — **default**; (2) its §3.1 LAW text AS PROSPECTIVE (R213); (3) LAW:145's clause — (a) the packet's, (b) the relayed rewrite keeping Furina's Companion→Fanfare loop legal. Supersedes E4's C1–C3 | OPEN — the Furina slice waits on these | reframe §9.1; burst-retirement §3.2; R220 A |
| `M54` | **Ask:** rule on the blind run's P3 — 0 of 10, and 0 of six Musters named a Memory consequence, so the base kit does not teach Rule 1. **Pick:** (1) print Rule 1 on the Muster's face or as a keyword, then re-run the gate; (2) change the starter Muster's dose; (3) accept the arm teaches Rule 2 only and re-scope to it; (4) hold and re-ask after a drafted-pool run. **Gate:** nothing ships off this run (R217 G) | OPEN — design call | kurage-memory packet §13.8; R213 step 2 |
| `M55` | **Ask:** rule on P4's half (b) — no play was named that would unblock a blocked front, the slot's trigger for the keyword ("Stir") to stop being optional. **Pick:** (1) build the keyword; (2) name the Charge sources on the strip; (3) both; (4) neither; (5) surface "Gain 1 Charge when a card of yours Exhausts" in the persistent Charge display — the bar's list, the strip being replaced. **Gate:** `M54` first | OPEN — design call | kurage packet §13.8, §11.3, §14 (in flight); R179 |
| `M56` | **Ask:** rule on the instrument gap — P2 and P6 grade a call against what the game did, and the sealed record carries the tester's words only, so both read SPLIT for want of it. Nothing was re-graded (R101b). **Pick:** (1) carry a per-turn wire snapshot in future records, these grades stand — **default**; (2) re-register both and re-run on `KURAGEMEM002`; (3) re-word both slots to grade reading only | OPEN — measurement call | kurage-memory packet §13.8; R101b |
| `M57` | **Ask:** prototype rows DO have a per-row description channel, so §12.6 item 14's "cannot be fixed from here" is wrong for one. **Pick:** (1) keep the loc merge — proven live, generated face stays wrong in the file; (2) take the `Localization` channel and delete the merge, removing the boot-path part `EB-194` came from; (3) both. **Gate:** it widens a generator contract | OPEN — generator contract | kurage-memory packet §13.6 |
| `M59` | **Ask:** rule the reframe's sixteen design picks `F1`–`F16` as ONE slate (R206/R212): Salon roster and slots, trigger and Evoke rules, Fanfare's Focus/cap/decay, the Rare drain card, legibility, starter. **Pick:** (1) take the packet's recommendation on all sixteen — **default**; (2) answer pick by pick at §9.2, where relayed review argues (2) on `F1`/`F13`/`F14`. **Gate:** `M52` — the architecture signs before its dials | OPEN — design slate | reframe §9.2, §6.3 slot 6; R220 A |
| `M60` | **Ask:** rule the Burst retirement's picks as ONE slate (R220 B). **Pick:** (1) `K1` *Sparks 'n' Splash* — Rare+stronger, Uncommon, Rare once-per-combat (Exhaust), or Rare with a capped spend; relayed review: rarity gates acquisition, not draw, so a repeatable spend-all eats every small sink; (2) `K2` the feeds; (3) `KO1` the fold, and if (a), `KO1a`'s payment rule; (4) `KO2` the Casket link. Options: §4.2, §4.3, §6 | OPEN — design slate | burst-retirement §4.2, §4.3, §6; R220 B/D |
| `M61` | **Ask:** pick how the Kurage memory element is built. Every look is answered, "also red" included — §14.5 proves it buildable, so the dimmed fallback is not carried. Mock: https://claude.ai/code/artifact/7f4b1180-306a-4740-a091-95b70020ad20 **Pick:** (1) a C# HUD element over the game's own pile viewer — **default**, no new scene, art or pck rebuild (§14.7); (2) a pck scene at the screen edge, own popup; (3) recolour today's gauge | OPEN — design call; gates `EB-198` | §14 |
| `M62` | **Ask:** fix the criterion that retires the fresh-Opus control form from every packet to the spot-check rate (R221 A). Measured: `KLEESPARK-R1` agreement **4 of 8**, pair read RETURNED the seat — the control stays on under every option. **Pick:** (1) retire at **≥ 6/8 over one round** — **default**; (2) ≥ 6/8 over two rounds; (3) only on the Codex seat's ADVANCE; (4) retire now. **Gate:** never mid-round | OPEN — measurement call | R221 A; R220 E/G |

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
