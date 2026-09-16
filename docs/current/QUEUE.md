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

**R250 (2026-09-04) closed `S4-G6` and `S4-G14` as OVERTAKEN:** both were
written against the shipped Kokomi kit, which the Plan overhaul (R240, R241)
retires; the prototype's own reads are its round packets, and a Balance-stage
band and protocol are drafted fresh when the overhaul reaches Balance.

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `fanout-picks-2026-09-16 4.7` | **CHOOSE** `EB-255`'s window: excluding starters by membership in `archetype_shares` moves `dominant_archetype` on two rosters, a `POLICY_VERSION` window and a re-baseline. (1) DEFAULT: fold it into the 4.5 window; (2) leave the lint red as debt. **Gate:** the 4.5 window. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.6` | **CHOOSE** whether the sim's act-2 Louse gets Curl Up 14 (the yaml says UNIMPLEMENTED; D5/D6 under #557 made the trigger real): it moves an encounter's difficulty. (1) DEFAULT: wire it at the same re-baseline window as 4.5; (2) leave it out. **Gate:** the 4.5 window. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.5` | **CHOOSE** when the twelve-arm table re-runs (`EB-195`, with `EB-74`'s staged lever): its gate EB-199 retired 2026-09-08, so only the measurement window binds (R101b: strike, never rewrite). (1) DEFAULT: at the next re-baseline window, with the Kokomi fold's; (2) now, on its own. **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.1` | **CHOOSE** whether a Skill may consume Vigor: Kurage's Oath (a starter Skill) printed Deal 7 under Vigor 8 and dealt 7, face and hit agreeing, and the game keys Vigor on the attack door, not the card type. (1) DEFAULT: the game's rule stands, `EB-441` closed; (2) retype Kurage's Oath as an Attack; (3) make Skill damage unpowered (drops Strength too). **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |

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

**R250 (2026-09-04) closed `M45` as OVERTAKEN:** its six calls were written
against the shipped kits and the richness playtest; the Kokomi items retire
with the overhaul, Spotlight was answered by R228, and anything of the Furina
items that survives returns through the reframe's own round packets.
**R265 (2026-09-07) ruled the three run picks at their defaults** (Klee's
Hexerei ownership and tag; Kokomi's queue, pool first), and the packets are
in `review/ruled/`.

**Nothing is open in this section.**

## 6. Prototype slices (R213) — held arms, re-authored kits, and the rules under them

Each row points at the packet section that carries the options in full; the
packet is the argument and this is the register.

**R270 (2026-09-08) ruled `klee-spark-purpose 5.1` at option (1):** Spark is a
currency, its income stays, and pool pass two gives it Block, cards and Energy
to buy, priced against Regent's Stars. The packet is in `review/ruled/`.

| ID | Decision needed | Status | Provenance |
|---|---|---|---|
| `fanout-picks-2026-09-16 4.8` | **CHOOSE** what to do with `EXPERIMENTS.md` registrations that now name deleted instruments (KLEESPARK-S1 after #535, the FURINAREFRAME rows after #561); the file is yours. (1) DEFAULT: leave them as published, the deletion's ledger line striking them; (2) strike them in the file with a one-line note. **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.4` | **CHOOSE** what the third companion set is now that EB-504/642/663 moved the ground: Witches' Circle keys off 'a Hexerei card', Noelle prints 'Klee's own Companions', a plain Companion card says neither. (1) DEFAULT: one printed name per set from a short design pass with Fable, then the sweep and a lint; (2) leave the three words. **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.3` | **CHOOSE** the curation of the inherited Silent relics and potions (census `review/active/inherited-potions-relics-census-2026-09-16.md`): Helical Dart and Snecko Skull mislead every kit, Ring of the Snake never rolls. (1) DEFAULT: drop Helical Dart and Snecko Skull from all three pools; (2) drop nothing; (3) replace them with kit relics, a design pass. **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `fanout-picks-2026-09-16 4.2` | **CHOOSE** whether Guest Cast multiplies a granted rider: delayed and conditional Companion legs print the multiplied number (#567); Kujou Sara's 'next Attack deals 4 additional' is not multiplied, and 6 would move a shipped card's strength (`EB-388`). (1) DEFAULT: leave it; (2) multiply every granted rider, one commit. **Gate:** none. | OPEN 2026-09-16. | review/active/fanout-picks-2026-09-16.md |
| `klee-opening-bank 5.1` | **CHOOSE** the opening Spark bank, round 26 finding the pass's Regent prices bind only on turn one where the bank is 1: (1, default) open every combat at 3 Sparks (Regent's Divine Right), rule 4 changes, [USER] plays; (2) reprice the six sinks to Klee's bank (1/1/1+1/2/2/4), rule 4 untouched; (3) as it is, one more lane. -> review/active/klee-overhaul-round-26-2026-09-08.md | HELD — gated on the consolidated pool's first read (R271 §3) | Klee r26; R270; R271 |

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

## 7. The Teyvat run frame (R272)

**R273 (2026-09-14) ruled the nation mapping at both defaults:** act 2 is Natlan or
Inazuma, act 3 is Fontaine or Sumeru; act 1 was confirmed Mondstadt or Liyue; the
Abyss is reserved as the act-4 face; Nod-Krai and Snezhnaya are later faces
(`EB-757`). The packet is in `review/ruled/`.

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
