# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start**. One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).
> **Row shape (R177):** a row is **the executable action, its acceptance
> condition, and the owning code area**, with at most one evidence pointer.
> Diagnosis and investigation narrative live in code, tests, a packet, or
> commit history — never in the cell; the commit that trims or closes a row
> preserves the old prose in history by construction.

> **Resolving a provenance identifier.** `eng-backlog`, `dockets/…`,
> `user-queue` and the retired sprint docs read at
> `git show pre-simplification-2026-08-06:<path>`. The two recap registers —
> `missed-requirements` and `open-playtest-items` — left HEAD after their
> rows migrated here; read them at
> `git show aa09b97:docs/current/backlog/missed-requirements.md` and
> `git show aa09b97:docs/current/playtest/open-playtest-items.md`.
> **`aa09b97` is NOT fetchable from `origin`** — it is a merge commit that no
> ref points at any more, so `git fetch --depth=1 origin aa09b97` fails.
> It is present in the local object store of any clone that has it, and
> `git show aa09b97:<path>` works there directly; on a clone that lacks it,
> fetch the tag instead and read the pre-migration copy.

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-71` | **Sly grammar standardization (`S4-G19`, ruled 2026-08-10 — R174).** The two near-identical mechanics become one. Scope, sim-side only: unify on the standard grammar, fold `sly_this_turn` into it, make Master Planner's grant speak the unified form, and update the extract pin that names the old shape. No C# leg is in scope here — parity follows once the sim form is settled | user-queue §2; `docs/archive/tech-debt-audit-2026-07-26.md` §5; R174 |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-82` | **`damage_per_exhaust` relic hook.** `EB-68` converted five of the seven flagged events; **Grave of the Forgotten** is not blocked on Enchant any more (Soul's Power is built and its lock condition is the eligibility rule) — it is blocked on **Forgotten Soul**, *"whenever you Exhaust a card, deal 1 damage to a random enemy"*, which wants a `damage_per_exhaust` hook the engine lacks. The event-relic admission rule forbids inventing it inline, so it is its own item. Build the hook, then convert the event | `EB-68` close-out; `790fb80`; `tier05/tests/test_r82_enchantments.py:328-338`; `docs/current/dossiers/content/event-conversion-gallery.md`; R159 |
| `EB-83` | **Wood Carvings' remaining blockers.** The last unconverted event of `EB-68`'s seven, blocked three ways and only one of them Enchant: **Slither** randomises cost **on DRAW** — new machinery, not a rider, so it is named in `enchantments.UNEXPRESSED` rather than approximated; and **Peck** and **Toric Toughness** are named base-game colorless cards no pool here ships. Two of three options is not a conversion, so all three legs are in scope: the on-draw card hook, and the two colorless cards | `EB-68` close-out; `790fb80`; `tier0/content/enchantments.py` `UNEXPRESSED`; R159 |
| `EB-84` | **The C# enchantment leg.** `EB-68`'s row deferred it explicitly — *"the C# leg follows the settled vocabulary"* — and the vocabulary is now settled and shipped sim-side (`61b8f4a` + `790fb80`, `RUNTEMPLATE 10`). **No C# enchant surface exists at all**: no decoration on the card model, no per-instance `enchant_damage` / `enchant_effects` twin, no event-side deck-level enchant op. Parity item, scoped to the shipped vocabulary and nothing beyond it | `EB-68` close-out; R82; R159 |
| `EB-69` | **`EB-22` execution — REVISE-ADOPT, ruled 2026-08-10 (R157).** Assist is a real third plan; the **A4 + A6 package** is adopted; **A3 / `discard_dividend` is DROPPED**. The fill is **14 cards landing at 74** (5 / 31 / 25 / 14) — *not* the packet's 76 headline, which was arithmetic against the dropped item. **Complete upgrade rows are REQUIRED before anything lands.** Names are provisional pending the `S4-G11` eye-read. Land as **one batch**, then rebaseline — this takes **measurement window 1**, ahead of `EB-26`'s. Includes the collision re-check against the live sheet | dockets; `docs/archive/brief-kokomi-pool-fill.md`; R157 |
| `EB-70` | **`EB-27p` starter-offer retune (ruled 2026-08-10, R160).** The personal-pool companion enters as an **optional, visible run-start offer**, classified into the already-shipped **randomized-starter** family and implemented by **retuning the starter seam** — explicitly NOT new Neow machinery. **Klee-only** until other characters get signature companions (that is later design, not this row). LAW's personal-pool kit clause carries the matching amendment: the offer is **declinable**, on the Ancient-door analogy | eng-backlog §4; R134; R160 |
| `EB-72` | **`M13` distribution printer + registration draft (ruled 2026-08-10, R164).** Two legs: (1) a **distribution printer** for the regret reads — the pooled emitter emits no percentiles by design and the route-regret block is unprinted, so there is today nothing to pre-register against; (2) a **pre-registration draft** for the `ROUTE_REGRET_MARGIN` / `draft_regret +1.0` measurement, for [USER] countersign at QUEUE `M13`. `+1.0` is **not** ratified and must not be treated as derived | EB-16w close-out 2026-08-07; R164 |
| `EB-74` | **Kokomi lever-2 candidate — BUILD, DO NOT PULL (ruled 2026-08-10, R154).** Construct a legal lever-2 candidate for the general power lift, complete and machine-checked, and **pull nothing**: the pull decision waits on the post-wave observation at QUEUE `S4-G13`. Suspected target named in the ruling — assist's missing internal payoffs | user-queue §2; R154 |
| `EB-78` | **`X9` workshop prep packet — numberless (ruled 2026-08-10, R163).** Workshop a **bounded per-turn read budget** for Kokomi's charge bank. **State no number** — the workshop sets the shape, [USER] prices it. Scope: Garment, Kurage, and the two pilot valuation sites. **Charge itself stays uncapped and unspent** (already LAW; not reopened). `moonlit_offering+`'s infinite loop is a **termination-hygiene defect handled independently** and is not part of the budget question | dockets/kokomi-workshop; R163 |
| `EB-81` | **`S4-G7` options packet.** Lay out the two remedies the 2026-08-10 ruling named — **rebalance the weak plans until they are viable** vs **expand salon to contain multiple archetypes** — as a decision packet: what each costs, what each moves, what each forecloses. It feeds the direction pick at QUEUE `S4-G7`; it takes no position | R153 |
| `EB-28` | The drafter's salon-deploy blindness — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible | eng-backlog §4; missed-requirements §3.6 |
| `EB-32` | The pilot block-panic rung — a pilot behaviour change that "would move every tier-0.5 number on one observation" (the one-observation basis is stated at the source), so it lands under a POLICY version bump | eng-backlog; routed from QUEUE 2026-08-08 (R136) |
| `EB-33/34/35` | Pilot/drafter repricing exhibits (The Gallery Stirs 0.0 offer; Vulnerable-as-flat-debuff; `_reaction_value` has no defensive term) — filed as inputs to a `_static_power` / reactions-promotion repricing session; the session's pricing calls go to [USER] when it convenes. **Note for whoever convenes it:** `EB-33`'s acceptance criterion from R96 — *"DRAFTER 13 is not done while The Gallery Stirs scores 0.0 at offer"* — was written against `DRAFTER 13`, was never discharged before the bump to `DRAFTER 14`, and so needs restating against the current drafter rather than being read as-is | eng-backlog; routed from QUEUE 2026-08-08 (R136) |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED, HELD.** Drafter behaviour change (`DRAFTER 15`) + re-baseline sweep; `Q18` countersigned, pinned DRAFTER 14. **Lands as step (5) of a fixed six-step order** — must not land before blind-first grading (4) or it invalidates the registration | eng-backlog §6; R121 |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-77` | **Produce the R89 draft — Furina summon-damage numbers.** `EB-53` has cited "the R89 countersign" as on the critical path since the playtest-4 triage, and **no draft exists in HEAD**: there is nothing to countersign. Draft the summon-damage numbers and their derivation for [USER] countersign; the `EB-53` Furina leg unblocks on it and nothing else | `EB-53`; playtest-4 triage §N1; routed 2026-08-10 (R169) |
| `EB-14` | `selectors` is bot-feed only — a mod-side hook into the selection screens is the open item | eng-backlog §2 |
| `EB-53` | **The N1 attribution pass — remaining legs only.** The end-of-turn docket (Bake-Kurage + burst visibility, one widget) is BUILT and LIVE-VERIFIED 2026-08-08 on package `0.2-634` — `Vfx/TurnEndPreviewBridge.cs`, `pck-src/shared/turn_end_docket.tscn`, firing order pinned via `Powers/TurnEndAttribution.cs`; presentation-only, declared UNMIRRORED. 6 of 9 captures taken, manifested in the packet §7. **Still owed, engineering:** `C5` (one better Klee run — three died at 24/32/37 of the 40 the Burst meter needs); `C6`'s co-op half (the bridge drives singleplayer only); the DISPLAYED firing order (never exercised — only one source ever stood at once). `C7` is unreachable as written — QUEUE `M16` owns that call. **Still [USER]:** `17a`, the eyes-on judgement of the six captures. **Still gated:** Furina summon numbers (the R89 draft is produced by `EB-77`); Klee bomb variety (rework-scoped design). **Folded-in live checks for the same session:** `never_reduces` apply-mode (`EB-26` `D2`), the `♪` glyph in the two renamed Barbara titles, the six renamed companion titles reaching a deployed package | playtest-4 triage §N1 (tag copy); refiled 2026-08-08 (R136) → review/active/livegame-captures-2026-08-08.md §7 |
| `EB-65` | **Seven Furina power sigils render the red `NOPE` missing-texture badge** — `res://furina/powers/{fortissimo_guard, stagehands, stagehands_encore, courtroom_drama, the_gallery_stirs, quick_change, unheard_confession}.png` are absent from the pck, and `KleePck.Path` falls through to the base getter while a file is missing. Diagnosed by measured elimination live on `0.2-612` (the §3 frame is `Fortissimo Guard` / `SalonDeployBlockPower`). The art is already produced — the candidate rows are in the art-runs bundle and the pick is [USER]'s (QUEUE Art debt). **Closes when the seven PNGs land, not before** | live-game session 2026-08-08 → review/active/art-runs-2026-08-08.md |
| `EB-67` | **Kokomi's relic and power icons render the red `NOPE` placeholder** — `EB-65`'s mechanism, one character over: the pck's `kokomi/` block has no `relics/` or `powers/` entries at all. Captured live on `0.2-634`: `Pearl of Wisdom` (character select + in-run) and the `Bake-Kurage` power badge. Asset gap, not a code defect — the art production is the item | live-game session 2026-08-08 (EB-53 capture run) |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-73` | **`art_lint` approved-exception mechanism (`M8.3`, ruled 2026-08-10 — R151).** The M8 ruling allows **one** hand-cropped `Character Details` Rare for Kokomi. `art_lint` bans that source outright, so the allowance needs a machine-readable approved-exception entry — the house pattern: a named allowlist row with its approval recorded, checked for rot, so the lint guards the exception instead of being edited around it. One entry, not a category | user-queue §10; `docs/current/art/kokomi-art-pass-requirements.md` §6; R151 |

## art — production work (the *picks* are [USER]'s in QUEUE; these are not)

| ID | Item | Provenance |
|---|---|---|
| `EB-76` | **`standing_ovation` CARD contact sheet.** The `ART-L12` duplicate pair `crowd_work` == `standing_ovation` cannot be resolved because there is no card-face sheet for `standing_ovation` to pick from — only the ICON sheet exists. Produce it, so the pick in the QUEUE Art-debt row has candidates. Production only; the pick is [USER]'s | `docs/current/art/kokomi-art-pass-requirements.md` L12; routed 2026-08-10 (R167) |
| `EB-36` | Three shipped cards render the BETA placeholder: `spotlight_center_stage`, `spotlight_guest_cast`, `confiscated` — zero `art/plan.tsv` rows. **Blind spot CLOSED** (2026-08-07): `art_coverage.py` billed from the sheets alone, so a C#-only card (the two selector halves) or a rarity:status token (`confiscated`) was neither COVERED, MISSING nor STALE — "art bill 0 missing" was true and wrong. The tool now takes a second universe from the portrait keys the shipped mod actually requests and bills the remainder; the three read as MISSING (271 covered / 274 expected) and `--strict` is honestly red until they land. **Remains: the hunt + the pick** (picks are [USER]'s — QUEUE art-debt row) | eng-backlog §6; missed-requirements §4.1 |
| `EB-38` | Animation Track F3 + the sprint-1 polish deferral — rest/merchant gentle idles both characters; in-combat layer approved and frozen but no polish sprint opened | eng-backlog §6; missed-requirements §4.5 |
| `EB-40` | **Author the Furina energy-counter SCENE — engineering half only; the art call is QUEUE `M19`.** Icons shipped 2026-08-08. There is no precedent: all three characters return the base game's `ironclad_energy_counter.tscn`. Hard constraints read from the shipped assembly: the scene root must carry `NEnergyCounter.cs` (hard `Instantiate<NEnergyCounter>` cast), satisfy `_Ready`'s five non-null `GetNode` targets, and fill `%Layers` with five orb-layer textures. Crash-class surface, no sim backstop, verifiable only in a live playtest. **GATED on `M19`** (the five-layer Hydro orb set). Kokomi has the same two gaps and is out of scope here | eng-backlog §6; furina-art-pass-requirements §8; split 2026-08-11 |
| `EB-52` | **(a) the fourth Fanfare evidence shape — still owed; (b) and (c) are STAGED.** Capture a Power being played and the Fanfare floor rising because of it, on one of the three RARE `gain_fanfare_floor` Powers, graded against red-pen Part 3. The instrument is confirmed live (the bridge publishes `KLEEMOD_FANFARE_FLOOR` beside `KLEEMOD_FANFARE` on every singleplayer GET — the read is one request either side of the play); **the obstacle is acquisition, bounded below by run survival under the bot policy** — two sessions drew six of the 19-pool rares and hit none of the three targets, an ordinary miss (P(0) ≈ 36%), not a shut door. Door odds, the reroll-loop constraint, and the per-run draw log are in the capture manifest §8 | S4-G16 + S4-G17 ops legs, routed 2026-08-08 (R136) → review/active/livegame-captures-2026-08-08.md §8 |
