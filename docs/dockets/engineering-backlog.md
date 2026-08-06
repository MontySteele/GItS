# Docket — engineering backlog

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status:** DOCKET. Opened 2026-08-06 by the docs diet (Track Z, Z-3). **Zero
design authority.** Nothing here is scheduled, priced, graded or ratified.
Every row is *routed* — it has an owner-shaped home and no decision.

**What it is for.** Three of the repo's retired registers carried open items
that need **no [USER] ruling to start**: confirmed bugs, measurement defects,
instruments that were directed and never built, and freely-workable blocks.
Those are not queue items — the queue is for things that need [USER] — but
until now they had nowhere else to live, so they stayed in registers that had
stopped being maintained. This docket is their home.

**Migration rule used, stated so it can be checked.** Each row below carries
the **source document's own wording** for the item, and a citation to the
section it came from. Where an entry in the source ran to several paragraphs of
evidence, the *item statement* is reproduced here and the evidence stays at the
citation — the source documents are REFERENCE, kept in place, and nothing was
deleted from them. No number, ruling or verdict was reworded in either
direction.

**What is NOT here.** Anything that needs a reply, a ruling, a countersign, a
taste pick or table time is in `docs/registry/user-queue.md`, not here. Several
items below have a queue twin — the *work* is here, the *ruling that unblocks
it* is there — and each such row names its twin.

---

## 1. Confirmed defects, freely workable

| # | Item (source wording) | Source | Note |
|---|---|---|---|
| `EB-1` | **Punch Off crash — ~~SUSPECTED-OURS~~ RECLASSIFIED GAME-SIDE/SPINE-SIDE 2026-08-06** (Class-P, R119 / P-B item C-3, per `docs/archive/punch-off-crash-memo.md`: zero signal connects in our mod, the signal exists only in native `spine-godot`, our patch is a postfix past the raising frame; the OURS attribution was inferred-not-observed. R99/2's routing note provides for exactly this flip; the acceptance form below stays recorded, the animation stream keeps the watch). A run died inside a Punch Off event; `godot.log` ends mid-backtrace at `PunchOff.PunchEachOther` → `CreatureCmd.TriggerAnim` → `NCreature.SetAnimationTrigger` (Harmony-patched by `Vfx/CreatureAnimationRouter.cs`) → `CreatureAnimator.SetNextState`, with `Signal '_internal_spine_objects_invalidated' is already connected to given callable`. **Acceptance form:** this item is not done while seed **`8B97LMCL2F`** crashes in Punch Off. | `docs/backlog-2026-07-29.md` §1 "C# — animation stream" | Owner: the animation stream (R99/2). Queue twin: user-queue §5 row 10.6 (reclassification to game-side, and the note that the crash log has rotated out) |
| `EB-2` | **Salon upkeep vs All the World's a Stage income race** — two powers in the same `AfterPlayerTurnStart` broadcast with no guaranteed order (`SalonPowers.cs:352` vs `FurinaResources.cs:1122`); with the Ancient equipped at 0 banked Encore the tick rate is nondeterministic, and possibly per-seat in co-op. | `docs/backlog-2026-07-29.md` §1 "C# — P2" | Same seam as `NC-9` in the parity memo (turn-start broadcast ordering is a divergence *family*) |
| `EB-3` | **Two unlintable hand-written kit cards**: `LetThePeopleRejoice.cs:57–82` (bare `8m`, `/4`, `6` literals — CONST_RE can't see them, `ROSTER_DEFERRED` exempts the card) and `AllTheWorldsAStage.cs:49,68` (+5 Encore/turn, Furina's largest economy lever, outside the sheets entirely — no source of truth in either direction). Extend the parity gate or add sheet rows. | `docs/backlog-2026-07-29.md` §1 "C# — P2" | |
| `EB-4` | **Two p90s that disagree**: `run_metrics._percentile` interpolates, `elite_blitz._percentile` is nearest-rank *while claiming to match it*; five copies total. Also two `wilson` implementations with different return shapes. Unify each to one function; verify which convention the ratified band locks used before touching. | `docs/backlog-2026-07-29.md` §1 "Python sim — P1 measurement defects" | A measurement defect that biases reported numbers |
| `EB-5` | **The combat pilot's scoring weights are unstamped inline literals** (`tier0/pilot/policy.py:426–504`) — they move winrates like sheet values but live outside constants.py, parity, and version stamps. Move to constants + stamp; no behavior change. | `docs/backlog-2026-07-29.md` §1 "Python sim — P1 measurement defects" | |
| `EB-6` | **Error-laundering fixes**: `refpowers.py:1130` bare-except mislabels loader bugs; `render_card_gallery.py:215` swallows upgrade-diff failures; `card_distinctness_report.py:435` lets an unparseable pool become a passing gate; `extract_base_game_pool.py:528` records a wrong blocker reason; `exp_furina_strength.py:771` drops failed arms from comparison tables unmarked. | `docs/backlog-2026-07-29.md` §2 | Five independent small fixes |
| `EB-7` | **Waiver-set staleness tests** — `PENDING_UNDERSIZE` / `PENDING_BANNED_FAMILY` / `PENDING_RED_PEN` in `art_lint.py` only print and can only grow, unlike `KNOWN_IDENTICAL` which has a staleness test. Add the same guard; also stop the two image checks from `continue`-ing past unreadable files (:483, :532). | `docs/backlog-2026-07-29.md` §2 | |
| `EB-8` | **Cross-sheet strict-domination check** — the gate sweeps within sheet only, and the bare CLI prints `CLEAN` for two of six sheets; the Clorinde/Raiden pair was caught by hand. | `docs/backlog-2026-07-29.md` §2 | |
| `EB-9` | `tier0/tests/test_art_coverage.py::test_stale_file_is_not_counted_as_coverage` fails on any checkout without the gitignored art tree (`ImageGen/images/`) — the "have:" list it asserts on is empty in a fresh clone. Its own docstring warns about machine-dependent tests; it currently is one. | `docs/missed-requirements.md` "Ledger corrections", found-while-auditing | A machine-dependent test |
| `EB-10` | `tier05/route.py:13` documents `route_regret` as existing (see §2.1) — the docstring should stop advertising an unbuilt instrument. | `docs/missed-requirements.md` "Ledger corrections", found-while-auditing | The instrument itself is `EB-16` |

## 2. Understudy harness — traversal-layer defects, FILED NOT FIXED

Routed 2026-08-04 (R99/3). All three are debt #1's class (the wire's screen
protocol is the expensive half of the apparatus) and all three belong to the
**next traversal pass**, per the signed gate package. They are left unfixed on
purpose — *a harness every pass re-opens is a harness nobody can quote a clean
run from.*

| # | Item (source wording) | Source |
|---|---|---|
| `EB-11` | **Defect 13 — `no_action` on a state with no `state_type`.** The bridge answered mid-transition with no `state_type` at all and the driver filed a defect rather than re-reading. **FILED, NOT FIXED**, deliberately. | `docs/backlog-2026-07-29.md` §1; record `docs/sprint-track-b-curves-log-2026-08-04.md` |
| `EB-12` | **Defect 14 — `bridge_unreachable` by timeout with the process alive.** The wire stopped answering while the game survived the full grace period; the first time that kind was filed correctly rather than as a crash. One observation, **no reproduction**. **FILED, NOT FIXED**, deliberately. | `docs/backlog-2026-07-29.md` §1; record `docs/sprint-track-b-curves-log-2026-08-04.md` |
| `EB-13` | **Defect 15 — `no_progress`, the map↔rest_site bounce.** Two distinct fingerprints across twelve posted actions, cycling `map\|act 1\|floor 6\|hp 59` ↔ `rest_site\|act 1\|floor 7\|hp 59`: a rest site entered at full HP, left, and re-entered without the floor advancing. Seed `43MLG7MG9L`, committed-Salon soak `20260805-004135` run 3. **FILED, NOT FIXED**. | `docs/backlog-2026-07-29.md` §1; record `docs/sprint-track-b-gate-log-2026-08-05.md` |

**Four things `UND-P1.5` did NOT close**, listed because a "BUILT" heading
invites the assumption that it did (`docs/backlog-2026-07-29.md` §2):

| # | Item (source wording) | Note |
|---|---|---|
| `EB-14` | `selectors` is **bot-feed only** — a declared asymmetry beside `potions_used`. A selector cut is a bot-feed cut until a mod-side hook into the selection screens lands. That hook is the open item. | |
| `EB-15` | the seed's `lobby` route **never fired** in three live runs; `debug_override` carried all of them. The lobby arm is retained and reports itself, but nobody should read "two routes work" out of this. | |
| — | `understudy/replay.py` **name collision** — which module the spec meant is a red-pen question | **Not here: it is a [USER] ask.** user-queue §5 row 10.5 |
| — | the live salon **cap** is now on the wire; the salon **member roster** is not. Nothing needed it. | Recorded, no work implied |

## 3. Instruments directed and never built

Each row is an instrument some ruling or gate depends on. Migrated from
`docs/missed-requirements.md`, whose Tier 2 heading states the class:
*"instruments and telemetry that rulings or gates depend on."*

| # | Item (source wording) | Source | Why it bites |
|---|---|---|---|
| `EB-16` | **`route_regret` — advertised in code, never written.** `tier05/route.py:13` *documents it as existing* but `tier05/run_metrics.py` defines no such function; repo-wide the name exists only in prose. | `missed-requirements.md` §2.1 | §3.7.5's "relics are underpriced" finding rests on exactly the comparison `sts2-map-and-events-research.md` §4.2 says needs this instrument to be readable |
| `EB-17` | **Klee: played-when-drawn / dead-in-hand / force-first-copy telemetry.** Zero matches for `played_when_drawn` / `dead_in_hand` / `force_first_copy` across `tier0/`, `tier05/`, `tools/`. | `missed-requirements.md` §2.2 | It is a **live gate**: bodyless draw/resource engines may not be buffed without it |
| `EB-18` | **The mod's per-fight telemetry (C2) was never built.** JSON-lines per fight (reactions by type, detonations, sparks, burst cast, damage by source, HP delta, turns), "in the slice from day one"; `tier1/analyze.py` reads per-**run** RunHistory, a different granularity. | `missed-requirements.md` §2.3 | A per-fight detonation counter answers the corpse-detonation question (`S4-G15`, queue `Q11`) for free |
| `EB-19` | **The sim-pipeline-step → C#-hook sweep is still owed.** Three separate parity defects (Superconduct, Shatter, aura tick ordering) reduce to PRE/POST hook misplacement; *"no pass has ever systematically mapped each sim pipeline step to its C# hook. That sweep is owed."* | `missed-requirements.md` §2.4; `klee-mod/DECISIONS.md:1421` | `NC-9`'s broadcast-ordering family is the same seam seen from the other side |
| `EB-20` | **Instrumentation for D8** (Encore economy census: 19/78 cards grant, 1 spends, absorption automatic) — measurement is open even though the lever is ruled-direction, unpicked. | `docs/backlog-2026-07-29.md` §2 | |
| `EB-21` | **`char_facts` baselines for Defect, Necrobinder and Regent — next local session.** `game_ref/` has a card baseline for all five characters but a `<char>_char_facts.yaml` for only two, so the patch sentinel's `characters` surface reports the other three as **"not watched"** rather than as clean. Cheap, no design content. | `docs/backlog-2026-07-29.md` §2 (queued 2026-08-05, R105) | |

## 4. Content and balance work with no ruling in front of it

| # | Item (source wording) | Source | Note |
|---|---|---|---|
| `EB-22` | **Kokomi pool fill to parity** — measured 61 cards vs Klee 76 / Furina 82, rares 10 vs 15. Draft the ~15–17 cards (rare-weighted) for red-pen; ratification is [USER]. | `docs/backlog-2026-07-29.md` §2 | Brief: `docs/brief-kokomi-pool-fill.md`. Ratification is a queue item, the drafting is not |
| `EB-23` | **Co-op divergence brief** — the Encore saturation divergence survived the pilot-gap sprint (pilot ruled out; dry rate 47.9% unmoved) and was routed to "co-op seat dynamics, via a future brief" that doesn't exist. Write it; fold in the co-op bug census above and the guest pilot's "extremely confusing" UI note. | `docs/backlog-2026-07-29.md` §2 | |
| `EB-24` | **Dead riders proposal** — `the_final_verdict` 0/298, `blocking_notes` 31/2471; propose reworked conditions for red-pen. | `docs/backlog-2026-07-29.md` §2 | |
| `EB-25` | **Lagavulin Matriarch's Soul Siphon half (player stat-drain)** — "the single highest-leverage backlog item for boss identity"; §10.8 already measured the consequence (she is the *softer* Act-1 boss, 94–97% win-given-reached vs Vantom's 67–85%, because her anti-turtle teeth are missing). No stat-drain op anywhere in `tier05/` or `tier0/engine/`. | `missed-requirements.md` §3.1; `run-model-rework-plan.md` §10.9 | Silently biases the Act-1 boss split every act-funnel number is read against |
| `EB-26` | **Kokomi P4: prevention on curve** (an uncommon lesser ward). P1/P2/P5 landed in v0.3; P4 did not — the only `prevent_exhaust_ward` in her pool is `vigil_of_the_deep`, **rare**. (Related, weaker: P3 "a ticking body for the commander" — no persistent recruit above the basic `bake_kurage`, and neither P3 option was ever explicitly chosen.) | `missed-requirements.md` §3.2 | Feeds `dockets/kokomi-workshop.md` |
| `EB-27` | **Two tier0.5 spec features: `choose3` slot mode and the Prune signature event.** `tier05/model.py:246-250` raises `ValueError` on a standalone `choose3` (it exists only as pity's payload); no event in `tier05/events.py` offers Prune. Nothing records the spec items as dropped. | `missed-requirements.md` §3.5 | |
| `EB-28` | **The drafter's salon-deploy blindness** — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible (§6(d) of the rework plan; the sibling AoE blindness was fixed, this one wasn't). | `missed-requirements.md` §3.6 | |
| `EB-29` | **Out-of-scale boss audit** (`test_subject`, `knowledge_demon`, `kaiser_crab`) — `test_subject`'s sheet inflates HP to stand in for a skipped mechanic (*"P3 Intangible skipped (the 300 bar carries the weight)"*), which is the fake-it-quietly pattern the house rules forbid. Still verbatim at `tier05/content/act3_pool.yaml:217-222`. | `missed-requirements.md` §3.9; `tier05-perf-and-ironclad-act3-notes.md` §1.5.2 | |
| `EB-30` | **The Ancient card's 3 Charge/turn is unmeasurable** — it lives in a layer the run sim does not model. The single least-defended value in Kokomi's build. | `open-playtest-items.md` §6.3 | Table fallback: if the Darv event offers it, take it and say what happened |
| `EB-31` | **Orobas is not modelled in the sim**, a recorded divergence. **NARROWED 2026-07-26** — Klee's variant *is* modelled now (`touch_of_orobas_klee`, real `combat_start_spark` hook, queue 2). Still unmodelled: Furina's R2 upgraded form and Kokomi's variant. | `open-playtest-items.md` §6.3 | |

## 5. Pilot and drafter observations routed by the Understudy Phase-0 measurement

Four observations from one nine-floor run driven through the real game.
**All four are notes in a queue, not open work**: nothing in `tier0/pilot/`,
`tier05/` or any sheet was touched by the sprint that filed them. Routed by
R93 (item A) and R96 (items B–D); full context
`docs/understudy-phase0-report.md`. Migrated verbatim as a block from
`docs/backlog-2026-07-29.md` §1.

| # | Item (source wording, abridged to the statement) | Note |
|---|---|---|
| `EB-32` | **[pilot-improvement] The block-panic rung never asks whether the Block on offer can matter.** Observed board: **39 incoming, a Frail-reduced 4 Block available, and a 25 HP enemy that exactly 25 damage in hand could kill** — the rung asked for the 4 Block on five consecutive decisions, while the kill deleted 15 of the 39 permanently. | **Nobody changes `tier0/pilot/policy.py` for this now** — it would move every tier-0.5 number in the repo on one observation. A scheduling decision; queue twin is the DRAFTER-world question, user-queue §2 `S4-G9`-adjacent, backlog §3 item 6 |
| `EB-33` | **[DRAFTER 13 — regression fixture] `score_offer` returns exactly 0.0 for The Gallery Stirs.** **Acceptance form, per R96: DRAFTER 13 is not done while The Gallery Stirs scores 0.0 at offer.** | The cheapest available acceptance test for the repricing |
| `EB-34` | **[`_static_power` repricing session — exhibit] `score_offer` prices Vulnerable as a flat debuff** (`amount * 2` through `_static_power`), so it cannot see a multiplier applied to an engine that is already producing damage every turn. Observed at a floor-4 draft: Usher the Waves scored 7.58, Charlotte 1.83. | Second exhibit for a session that already has one |
| `EB-35` | **[reactions-promotion session] `tier0.pilot.policy._reaction_value` has no defensive term.** Observed: a Cryo-into-Hydro reaction survived a telegraphed 24 for roughly zero cost while the pilot wanted 5 Block. This is **"reactions are weather, not strategy" appearing inside the pilot's own head**. | Third independent sighting of the same disease, first from inside the code |

## 6. Art surface — production work (the *picks* are [USER]'s, these are not)

| # | Item (source wording) | Source | Note |
|---|---|---|---|
| `EB-36` | **Three shipped cards render the BETA placeholder and are invisible to the coverage tool**: `spotlight_center_stage`, `spotlight_guest_cast`, `confiscated`. Zero rows in `art/plan.tsv` for any of the three. **Structural blind spot:** `tools/art_coverage.py` bills from the canonical sheets, and these are a C#-only selector pair plus a token. | `missed-requirements.md` §4.1 | Needs a plan.tsv row and a hunt |
| `EB-37` | **The character-icon `_outline` asset was never produced.** No outline row in `art/plan.tsv` or `art/SOURCES.tsv`; `Klee.cs:146`, `Furina.cs:84`, `Kokomi.cs:134` all return the *fill* `char_icon.png` for `CustomIconOutlineTexturePath`. | `missed-requirements.md` §4.2 | Also user-queue §8 (art debt) |
| `EB-38` | **Animation Track F3 and the sprint-1 "polish sprint" deferral** — rest/merchant gentle idles, both characters; behind it, sprint-1's Non-goals deferred the `selection_screen` / merchant / rest-site / `card_trail` convention scenes "to a polish sprint after the in-combat layer proves out" — the layer is approved and frozen, and no polish sprint was ever opened. | `missed-requirements.md` §4.5 | |
| `EB-39` | `no_holding_back` still uses the `Klee Multi Wish` source that L6 flagged as trimming 76% of the image — the same clipping round 3 rejected for `the_big_one`. | `missed-requirements.md` §4.6 | |
| `EB-40` | Furina's energy counter: `Furina.cs:97` still points at `ironclad_energy_counter.tscn`, and `energy_icon_74/22` have no plan rows. | `missed-requirements.md` §4.6; `furina-art-pass-requirements.md` §8 | Listed because the blocker scene is easy to lose |
| `EB-42` | **Path B (Skeleton2D) animation spike — a normal Code sprint, ruled 2026-08-06.** [USER], verbatim: *"Let's do FREE-SPIKE and reconsider if the results disappoint."* Kokomi is the pilot (`docs/archive/animation-capability-memo.md` §5); the computed-weights-from-layer-masks idea rides with it (memo §2b); **Path C layered remains the shipped fallback throughout.** **Reconsider trigger, recorded verbatim per the dispatch: disappointing spike results re-open the Spine licence question ($379 Pro; Essential cannot author meshes) without a new sitting.** The "animation path session" has left the design queue | `docs/dispatch-2026-08-06b-eleven-replies.md` §1 (Animation); R118 | Queue twin: user-queue §1 "Already answered" (FREE-SPIKE row) |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED PENDING 10.7, ruled 2026-08-06.** [USER] on 10.3, verbatim: *"Yes"* — payoff-presence extends to the spotlight limb (`tier05/draft.py`); `limelight` alone stops satisfying the limb. **The sequencing rail, recorded per the dispatch:** this is a drafter behaviour change = **DRAFTER 15** + a re-baseline sweep under stamp law; the payoff-reach sprint's pre-registration (whereabouts unknown; the 10.7 search is running, Track S2) was registered against a specific drafter version, so landing D15 before that document is found and its pinned drafter version read could invalidate a blind pre-registration — the exact thing the escrow discipline exists to prevent. **HELD until 10.7 resolves**: D15 lands immediately after, either once the sprint runs under its registered version or after a clean re-registration if the document is truly lost. No prediction is read, nothing re-litigated. The staged branch is Track V's (pushed unmerged, never landing this wave). **UPDATE 2026-08-06 — the 10.7 search is COMPLETE, NOT FOUND (Track S2): the "found" branch of this rail is dead.** The document was most likely never a repo file and no pinned drafter version can ever be read. D15 now waits on the **re-registration** (`docs/payoff-reach-reregistration-draft-2026-08-06.md`) being countersigned — user-queue row `Q18` — and the payoff-reach sprint running under it. **UPDATE 2026-08-06 — `Q18` is COUNTERSIGNED** (dispatch (e) / R121; [USER] verbatim *"agreed, countersigned, tto quarantined."*). The registration is live, pinned **DRAFTER 14**, predictions blank-by-design until the kickoff commit. **D15 is still HELD, and its place is now fixed rather than open-ended: it is step (5) of a six-step order in which no step reorders** — predictions authored (2), the sprint runs under D14 (3), blind-first grading (4), *then* **D15 lands with its re-baseline** (5), and only then does the quarantine lift (6). Landing D15 before step (4) would invalidate the registration this row exists to protect | `docs/dispatch-2026-08-06d-four-replies.md` (10.3); R120; `docs/dispatch-2026-08-06e-six-replies.md` (`Q18`); R121; user-queue §5 row 10.3 (struck) + row `Q18` (struck) | Sibling precedent: `staged/f14-siblings` |
| `EB-44` | **`docs/animation-spike-skeleton2d-kokomi-2026-08-06.md` carries no lifecycle banner** — a defect against the Z-1 law (every `docs/` `.md` says how it is maintained). **Class-P DOUBT, deliberately not fixed by the purge (P-B, C-10): choosing the status IS the judgment.** REFERENCE (a findings record) is likely, but `EB-42` makes the Skeleton2D spike a live Code sprint and the LIVING budget grants one charter per active sprint — whether this doc is that sprint's charter or a closed record depends on Track AN's state. Whoever runs Track AN next stamps it | `review/stage-clear/class-p-candidates.md` C-10 | Mint 2026-08-06 (P-B); one line to close once Track AN's state is known |
| `EB-45` | **18 archive-internal dead sibling pointers — a policy input for the Clear-the-Stage move track (R-B), not a fix.** `docs/archive/*` files cite each other at pre-move root paths (full list: `review/stage-clear/citation-graph-notes.md`); rail 1 forbids editing frozen text, so they are unrepairable at the citer and tolerated since their moves. **Class-P DOUBT (P-B, C-11): nothing false is asserted by a frozen record about the world as of its date, and no one-commit fix respects rail 1.** The live question is R-B's move policy: accept the same staleness for the next wave of moves, or leave ledger-/archive-cited files in place (`review/stage-clear/refactor-plan.md` §R-B takes the second answer for ledger-cited files) | `review/stage-clear/class-p-candidates.md` C-11; `review/stage-clear/citation-graph-notes.md` | Mint 2026-08-06 (P-B); discharges when R-B's policy is written down |
| `EB-46` | **Why did tag-visible scoring lower the anchor's winrate (11.13% → 7.50%)?** — minted verbatim 2026-08-06 by [USER] (dispatch (e) / R121, `Q19` SHIELD). [USER]'s words, verbatim: *"plus a note for any future sim work to take a look and figure out what went wrong (why did winrate go down, basically)"*. The observed fact: R118's 10.2 rider gave `ref_ironclad`'s `archetype_package` `Card.archetypes` tags for instrumentation, and the tags also reached the drafter (`draft.core_complete` gates `plan_live`; `_core_progress` feeds `score_offer`'s +3.0 core-advance bonus). In the paired v5↔v6 halves of the same battery — same seed, same n — the anchor moved **win 11.13% → 7.50% (z = −4.84)** and **act-1 71.23% → 64.77% (z = −5.37)**, the only arm past Bonferroni in an otherwise unmoved 12-arm sweep. **A diagnosis question for future sim work: no deadline, no design authority, nothing scheduled by this row.** It does not gate the SHIELD repair, which is separately ordered by the same reply. Related tripwire, recorded at R121 rather than here: if the shielded re-measurement does not restore the archived ordering, the track stops and surfaces — that would mean the mover wasn't the tags, and this row becomes the live question rather than a note. **UPDATE 2026-08-06 — THE TRIPWIRE FIRED; this row is now the live question, not a note.** The SHIELD landed (`draft._core_advance_view`, branch `findings/track-e5-shield`) and the `ref_ironclad` arm was re-measured under the table's own recipe (n=3000, seed 20260729, `RT7/D14/P3/C6`, checkpoint `review/r121-shield/shielded-arm-9.json`): **win 13.83% [12.64, 15.12]**, act-1 72.47%. That does not restore the archived ordering — it **overshoots** it: **z = +3.16 vs the archived 11.13%** (past the sweep's 12-arm Bonferroni bar of 2.87) and **z = +3.08 vs `furina/salon` 11.20%**, whose interval it no longer overlaps, so the anchor moves from archived **co-leader** to **sole leader**. A second, diagnostic-only reading (`review/r121-shield/probe-full-shield.json`, NOT committed behaviour) shields the WHOLE of `score_offer` — i.e. the scorer sees exactly the pre-rider cards — and still reads **13.20%** (z = +2.45 vs 11.13%), which says the residual is not a leftover tag-reading term in the scorer. **The open question this row now carries:** the archived 11.13% is a **CONSTANTS 5** number and every shielded reading is CONSTANTS 6, so "the tags moved the anchor" and "C5→C6 moved the anchor" are confounded in the paired halves; the sweep's attribution rested on the other eleven arms being unmoved, which does not establish that this arm was. An untagged-under-C6 reading never existed before these two, and both put it ~2pp ABOVE its C5 self. **UPDATE 2026-08-06 — [USER] ruled the tripwire, verbatim: *"Yeah, I think A) is defensible here."*** Of the three options surfaced — (a) land the shield and republish 13.83% with a dated confound note, (b) hold pending this row's diagnosis, (c) revert to ACCEPT — **(a) executes**: the `ref_ironclad` row is republished at the shielded reading and **the untagged-under-C6 number is the honest baseline going forward** (`docs/roster-anchor-v14-v6-2026-08-06.md`, "Republication note"; R121's dated addendum records the discharge). **This row is therefore no longer "why did the winrate go down" as originally posed — that question presumed the archived 11.13% was this arm's comparable predecessor, and it is not.** The question now is one clean thing: **separate the tag effect from the v6 (C5→C6) effect on this arm** — the two are confounded in the paired halves and the shielded readings put untagged-C6 ~2pp ABOVE untagged-C5, which the tags then more than reversed. Still no deadline and no design authority; nothing waits on it | `docs/dispatch-2026-08-06e-six-replies.md` (`Q19`); R121 + its 2026-08-06 addendum; `docs/roster-anchor-v14-v6-2026-08-06.md` ("Republication note" + "Factual note"); `docs/archive/v6-rebaseline-sweep-2026-08-06.md` (the mover section); `review/r121-shield/` (harness + both checkpoints) | Queue twin: none — `Q19` is answered and struck. SHIELD landed, re-measurement ran, tripwire fired and was **released by [USER] on option (a)**; the row is republished |

**Closed by this diet, recorded so it is not re-opened:** `missed-requirements.md`
§4.3, "the salon member sprite-scale fix was written up and never applied", is
**fixed** — `SalonVisualsBridge.cs` declares `SpriteScaleMax = 0.5f` and takes
`Mathf.Min(SpriteScaleMax, spacing / width)`, verified by Track Y (Y-7) when it
ratified principles v1.13, and asserted in
`tier0/tests/test_visual_contract_gaps.py`. The `AS2-D5` capture it blocked is
now unblocked and sits in user-queue §7.

## 7. Refactors — only if budget remains (big, safe, boring)

`EB-41`, migrated whole from `docs/backlog-2026-07-29.md` §2:
*"`run_one` 518-line split; codegen driver unification (F3, rolled forward
twice); telemetry-module template dedupe; `exp_*` script archive move;
`apply_upgrade` op-coverage guard."*

## 8. Discharged on migration — the rows that did NOT come across

Recorded so the next sweep does not resurrect them from the husks.

| Source row | Discharged by |
|---|---|
| backlog §1 "The drafter prices 42 of the engine's 56 ops at exactly zero" | **FIXED `3e3c243`** (2026-07-29); ledger entry **R107(a)**, which discharges `S4-G8` |
| backlog §1, ten C# defects incl. the Salon member counter clamp and the NRE soft-lock class | **FIXED `29f5ce6`**, deployed as artefact 0.2-247 |
| backlog §1 P2, Courtroom Drama's globally-consumed once-per-turn window; `CurtainCallHooks.Purge` missing `CompanionPlays` | **FIXED `29f5ce6`** |
| backlog §1 P3 cluster, six of eight | **FIXED `29f5ce6`** |
| backlog §2 "Kokomi stability-band instrument" | **ALREADY BUILT** — `run_metrics.stability_profile`, `DEC-D5` (2026-07-27); struck 2026-08-06 (R107, S4 finding F5). Only the *declaration* is open, and it is `S4-G6` in the queue |
| backlog §2 "Understudy P1.5 — the bridge fork: NEXT" | **BUILT 2026-08-05**; log `docs/archive/sprint-understudy-p15-log-2026-08-05.md`. Its four non-closures are `EB-14`/`EB-15` above and queue row 10.5 |
| backlog §2 "S7 probe (a) — the no-relic scripted block fight" | Registration is `docs/probe-a-block-offset.md`; the **countersign** is a queue item, not engineering work |
| backlog §2 "Docs de-drift, mechanical half" | **DONE by this diet** (Z-1/Z-3/Z-4): status banners on every document, the three scattered ledger-correction blocks folded, the Kokomi protocol re-pinned 2026-07-29 |
| backlog §2 "Deferred-but-solved audit" | Executed in spirit by this diet's §6 note (the sprite-scale fix was found already shipped); no separate sweep is owed |
| `missed-requirements.md` §1.4 (Kokomi multiplicative-read cell) | **CLOSED (R73/E1, 2026-07-26)** — `tier05/exp_neap_tide_e1.py` ran the cell; landed multiplier is 3 |
| `missed-requirements.md` §3.6 `SPOTLIGHT_BASE_MULT` | **CLOSED by R71** (2026-07-26) — 1.5 is law |
| `missed-requirements.md` §3.8 (Kaboom Beetle Swarm ruling) | **CLOSED (R72, 2026-07-26)** — option (b), bombed-state snapshots at cast. The printed-text thread is a queue item |
| `missed-requirements.md` Tier 5, two stale sheet comments | **BOTH FIXED AT SOURCE** — struck 2026-08-06 (R107, S4 finding F15) |
| `open-playtest-items.md` §6.1 `blazing_delight` plan row | **CLOSED 2026-07-26 (`6f1b969`)** |
| `open-playtest-items.md` §6.2 red-pen session / Furina starter upgraded form / Raiden disposition | **CLOSED 2026-07-26** — red-pen Part 1; R2 (queue 3, `477b282`); R52 |

## 9. Items that stayed in the queue rather than coming here

Listed so a reader who expected them here knows where they went. Each needs
[USER], which is the whole test.

`S4-G7` Furina items 1–3 · `S4-G9` the ratification batch · `S4-G10` shop
channel §7 close-out · `S4-G11` R29d naming/lore pass · `S4-G18` Klee pass-4
ask A3 · `S4-G19` Sly unification · `S4-G20` Standing Ovation boost expiry and
the sim-vs-C# salon RNG divergence · the Kaboom Beetle Swarm printed text ·
the ten-Spotlight-powers icon question · the enchantments design pass ·
Kokomi art §6 and v0.4 §6 rulings · `missed-requirements.md` §1.1/§1.2
(co-op Fanfare partner-flux, cross-player Spotlight passing — the "build or
waive" ask, backlog §3 item 8) · §1.5 (Furina Q3 innate-on-upgrade) · §2.5
(Klee ask A5) · §3.3 (`kurages_oath` = 12) · §3.4 (Klee's two dead-card
reworks) · §3.7 (Furina's A6 route ruling) · §4.4 (the Fontaine Rares sprint's
four close-out items) · Tier 5's process debts.
