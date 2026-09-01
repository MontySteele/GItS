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

> **NO NEW `M` IDS ARE MINTED AFTER 2026-09-01.** The M series stops; existing
> `M` rows close in place and are neither renumbered nor deleted. A new pick is
> named by its packet section until it is ruled, and by its `R` number after.
> This register holds [USER]'s A/B/C picks only: (A) a design direction a brief
> cannot settle, (B) eyes-on taste, (C) money, one-way doors, a staged balance
> lever, LAW or measurement-law amendments. D, E and F picks are applied by
> Claude at their default and disclosed, never recorded here
> (`CLAUDE.md` §Norms).

---

## 1. Kokomi — band, playtest, and levers

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G6` | **Ask:** declare Kokomi's HP stability band from design intent — never revisable against the playtest that grades it (D5). **Pick:** (1) Claude drafts it from written intent, countersigned before the confirmatory protocol — **RULED (R231)**; (2) at the table; (3) DARK. **Gate:** the exploratory run first, the confirmatory after (R175) | OPEN — mechanism ANSWERED (R231), the band still owed | user-queue §2; `DEC-D5` clauses 2–4; R156; R175; R212; R231 |
| `M69` | **Ask:** rule on `X9` — `W9` FIRED on Limb A: repeatable readers are **58.91%** of completed-turn reads (**51.68%** without `EB-242`'s pilot reads), both over R188's 50%. Severity QUIET (`p50` 0). **Pick:** (1) R188 STANDS, no read budget; (2) re-read after `EB-242`, then rule — **default**; (3) open a dedupe/cap options packet. **Gate:** `EB-242` for (2) | OPEN — the graded read is in | R188; R233; `charge-reads-per-turn-registration-2026-08-13.md` §5.4, §9 |
| `S4-G14` | **Ask:** run the Kokomi confirmatory protocol and rule on its written question list — an exploratory run cannot be graded, and this one fills the Answers block. **Eyes-on:** `docs/current/playtest/kokomi-playtest-protocol.md`, question by question. **Gate:** the sequence R175 fixed — post-wave exploratory run → `S4-G6`'s band declaration → this run; plus `EB-53`'s remnant | OPEN — table time | user-queue §2/§7; R115; R152; R175 |

## 2. Shop, pricing, and money

**R231 (2026-08-30) closed `M14` at option (1), NOISE.** The published trigger
result stands exactly as graded (R101b): only condition 4 fired, the mean Δ is
−0.07 pp with no interval separation and mixed character signs, and a
narrowly-crossed zero is not grounds for a redesign against a 20.7% slot-one
purchase rate. The affordability figures stay diagnostic context, not a finding.

**Nothing is open in this section.**

## 3. Eyes-on reviews and taste

**R231 (2026-08-30) closed three rows out of this section.** `S4-G11`, the
name/lore eye-read, was ruled in all three parts: *Backstroke* is KEPT (canon
already supplies *Pressurized Floe* and *Shattering Pressure*, so the invented
subtitle distinguishes without stealing); *Tengu Flurry* is KEPT and
`chinowa_ward` is RENAMED **`chinju_ward`**, anchoring to Chinju Forest instead
of an unexplained real-world ritual term; and the `EB-82` Grave conversion takes
the Liyue / Nameless Cairn labels. `M16` closed at option (1) — `SceneSlots`
stays at 4 as harmless headroom. `M19` closed at option (1) — **A Fontaine
Hydro** for Furina's five-layer energy orb, which lifts `EB-40`'s gate. Two more
narrowed rather than closed, and stand below.

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `S4-G12` / `CC-G1` / `CC-G2` | **Ask:** approve or veto the twelve Curtain Call faces and the A0 smoke, by eye. **Eyes-on:** the `S4-G12` sheet, regenerated over all six gate rows. The re-hunt set is **FOUR** (`warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`) — `standing_room_only` overturned and `grand_gala` displaced (R166); the A0 smoke is PARTIAL. **Gate:** none; materials produced | OPEN — materials ready | user-queue §2; `review/ruled/art-runs-2026-08-08.md`; R166 |
| `S4-G17` | **Ask:** three running-game looks, no full playtest. **Eyes-on:** `AS2-D5` the salon; `AS2-B5` motion and facing taste; `AS2-E2` icon picks (canonical in the Art debt row). **Gate:** none — captures are staged and manifested | OPEN — urgency reduced (hover-targets closed pt.4; B5 "not noticed") | user-queue §2/§7; `docs/animation-sprint-2-plan.md` (B5/D5/E2); `review/records/livegame-captures-2026-08-08.md` |
| `M26` | **Ask:** accept or amend the end-of-turn docket by eye (`EB-53` item 17a). **Eyes-on:** does the end of turn read legibly; is the per-seat position doing the attribution work; is the chip's prominence right. Frames in `art/eb52_captures/` and `understudy/logs/frames/`. **Caveat:** no frame isolates the electro (Oz) leg, so the pyro→electro ORDER falls to this look. **Gate:** none — 6 of 9 captures taken | OPEN — eyes-on | BACKLOG `EB-53` §7; live verification 2026-08-08 |
| S8 + S10 galleries | **Ask:** one body is left — **Globe Head**, whose silhouette is unresolved. R231 ruled RESKIN for the five verified bodies; execution rides the enemy-remap wave. **Pick:** (1) RESKIN; (2) REDESIGN — no default, the silhouette is the whole question. **Gate:** none; both galleries are written | OPEN — narrowed to Globe Head (R231) | user-queue §4; `dossiers/content/potion-relic-conversion-gallery.md`; `dossiers/remap/reskin-gallery.md`; R231 |
| Art debt | **Ask:** one pick is left — accept or replace `grand_gala` r6, which is provisional. R231 settled the other two (the sigil collision, and Kokomi's `Character Details 1` exception). **Pick:** (1) accept r6; (2) re-hunt. **Gate:** none | OPEN — narrowed to `grand_gala` r6 (R231) | user-queue §8; `review/ruled/art-runs-2026-08-08.md`; `art/kokomi-art-pass-requirements.md` §6; R167; R171; R231 |

## 4. Fontaine Rares close-out

**R231 (2026-08-30) closed `M10`: the Fontaine Rares close is APPROVED**, with
the v1.7 lore/naming audit riding on it, and **Neuvillette ships as-is**
carrying its later redesign. The four companion art picks continue to ship
under R212(1), veto on the sheet.

**Nothing is open in this section.**

## 5. Post-playtest design calls

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `M45` | **Ask:** ratify the pass's six open calls as ONE slate (R206). **Pick (adopt / defer, audit first):** (1) `salon_rotate` reader / timing; (2) `smoke_and_sparks` re-body / cut; (3) `Win10`/`Win11` on choices / state; (4) Spotlight: ANSWERED R228 = one mode, priced; (5) `depths_judgment` flat-14 / rescale; (6) Kokomi Block cluster accept / amend; (7) Charge lever: `S4-G13`. **Gate:** the playtest | OPEN — after the playtest | R206; review/ruled/richness-playtest-brief-2026-08-26.md |

## 6. Prototype slices (R213) — held arms, re-authored kits, and the rules under them

Each row points at the packet section that carries the options in full; the
packet is the argument and this is the register.

→ **`review/ruled/sitting-2026-08-30.md` is CLOSED by R224 (2026-08-30).**
Every row it covered has left this register — `M47`, `M49`, `M50`, `M52`,
`M54`, `M55`, `M56`, `M57`, `M59`, `M60`, `M64` — along with the Klee round-2
picks, the §14 direction and its migration branch, the Burst retirement's five
shapes, and Ceremonial Garment's acquisition (**LOOT**: draftable Rare,
`kit_card` and `requires: burst_energy_full` dropped, the kit-grant machinery
deleted outright). The packet's own §6 architecture paragraph and all eight
§3.2 LAW blocks are countersigned **AS PROSPECTIVE** — **no `LAW.md` line
moved**. The engineering it created is `EB-213`–`EB-219` in `BACKLOG.md`.
Two rows returned from it and both are now closed: `M65`, the re-ask R224 item
17 = (3) ordered, and `M66`, the C# prototype gate shape the relayed review
raised. **R225 (2026-08-30)** ruled the open-items slate: the top-level-cost
clause is amended to admit a mode-head price and *Bag of Tricks* proceeds
(`EB-224`); the single `PROTOTYPE_CARDS` switch stands, with a scope lint
(`EB-225`) and a three-fight soak on every dev deploy. **R227 (2026-08-30)**
then closed `M67` at option (1): Kokomi slice 2 RETIRES — its four
Charge-priced arms and their round-2 boards delete, the spend plumbing stays,
and the Charge question moves whole to the memory program (`EB-229`, then whole
fights). That row has left this register with the rest.

**R228 (2026-08-30)** then closed `M68`, the Furina Spotlight pick R226 owed
and R227 pick 4 started, at option (1) — **one mode, priced**: Center Stage
retires, Guest Cast and `SPOTLIGHT_BASE_MULT = 1.5` stay, and the selector aims
a Companion and costs Encore. `M45`(4) is answered with it. Nothing migrates
before the reframe's own whole-fight read, which was that row's gate and stays
true of the work as a sequencing fact.

**Nothing is open in this section.**

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
