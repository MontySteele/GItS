# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start**. One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).

> **Resolving a provenance identifier.** `eng-backlog`, `dockets/…`,
> `user-queue` and the retired sprint docs read at
> `git show pre-simplification-2026-08-06:<path>`. The two recap registers —
> `missed-requirements` and `open-playtest-items` — left HEAD after their
> rows migrated here; read them at
> `git show aa09b97:docs/current/backlog/missed-requirements.md` and
> `git show aa09b97:docs/current/playtest/open-playtest-items.md`
> (`git fetch --depth=1 origin aa09b97` first on a shallow clone).

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-17p` | Force-first-copy **paired** winrate — the register's actual phrase: two decks on the same seeds, one with a copy forced in, one without. Deck construction is barred from the tier0 kernel, so this is a tier05 experiment under EXPERIMENTS pre-registration. The fight-side half ships (`metrics.card_flow_profile`, `--card-flow`) and explicitly declines to call its within-arm split the pairing | fix-sweep-2; EB-17 residual |
| `EB-50` | Implement the scorecard's two invariants (≤4.0 A2 ceiling; A1+A6 elite pairing) as **report flags** — the M4 fork collapsed: the suite-failure branch is illegal under the descriptive-only axis closure and `test_axes_honesty.py:195-207` guards against reinstating it; today neither invariant is enforced anywhere | user-queue §10; M4 retired 2026-08-08 (R136) |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-28` | The drafter's salon-deploy blindness — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible | eng-backlog §4; missed-requirements §3.6 |
| `EB-32` | The pilot block-panic rung — a pilot behaviour change that "would move every tier-0.5 number on one observation" (the one-observation basis is stated at the source), so it lands under a POLICY version bump | eng-backlog; routed from QUEUE 2026-08-08 (R136) |
| `EB-33/34/35` | Pilot/drafter repricing exhibits (The Gallery Stirs 0.0 offer; Vulnerable-as-flat-debuff; `_reaction_value` has no defensive term) — filed as inputs to a `_static_power` / reactions-promotion repricing session; the session's pricing calls go to [USER] when it convenes | eng-backlog; routed from QUEUE 2026-08-08 (R136) |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED, HELD.** Drafter behaviour change (`DRAFTER 15`) + re-baseline sweep; `Q18` countersigned, pinned DRAFTER 14. **Lands as step (5) of a fixed six-step order** — must not land before blind-first grading (4) or it invalidates the registration | eng-backlog §6; R121 |
| `SKIP-10.9` | Living skip-backlog of un-modelled mechanics to promote when a pass needs them. **Enemy:** Back Attack (Kaiser Crab), untargetable Burrow (Tunneler), Ethereal/Hex auras (Knight Gang), pick-your-poison curse choice (Knowledge Demon), damage caps (Hard to Kill / Plating / Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards cadence intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor-power list (Imbalanced / Ringing / Paper Cuts / Stock / Galvanic / Rampart), Soul Siphon stat-theft class (the Matriarch's player-half drain landed with EB-25), and the two Ancient relic hooks — Blessed Antler and Philosopher's Stone. **C#-side structures with no sim twin (EB-19):** the deferred-settle machinery (`SpotlightSystem` PendingDraws / `CurtainCallPowers` NoteEncoreSpent / `FurinaResources` PendingDeltaBlock — parity rests on every flush site being reached; a stranded draw is the failure mode) and per-dealer reaction windows (ruled co-op divergence, red-pen R1; solo is byte-identical). *Restored to the full §10.9 open list 2026-08-06 — the migration had dropped ~14 entries, making logged approximations read as unlogged fakes (EB-29c)* | run-model-rework-plan §10.9; EB-29 audit |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-1` | **Punch Off crash** (reclassified GAME-SIDE/SPINE-SIDE) — the animation stream keeps the watch; not done while seed `8B97LMCL2F` crashes in Punch Off | eng-backlog §1 |
| `EB-14` | `selectors` is bot-feed only — a mod-side hook into the selection screens is the open item | eng-backlog §2 |
| `EB-47` | **Windows compile validation of the 2026-08-07 sitting's C#, plus R135** — six regenerated cards (`AriaOfRecompense` reverted to pure Encore; `TakeYourBow` gained the first upgrade-added `repeat_this` emission; `KuragesOath` gained a `PowerAmount` var where it had none; `StudyOfExplosions` and `SecretStash` gained damage bodies and `TargetType` changes; `LastingImpression` gained the `1_per_4_fanfare` Block clause — `HoverTips` using-directive, the three calculation vars and the `GainBlock` await, R135 2026-08-08) plus the hand-written `KaboomBeetleSwarm` description string. All were generated/edited on macOS where the mod cannot build; nothing here is compile-verified | R130–R132; R135 |
| `EB-53` | **The N1 attribution pass** — "End-of-turn attribution pass (cross-character, one pass not three)", the playtest-4 headline ask, consolidated from pieces already on the register. Four legs: **Furina summon damage numbers** — the R89 draft, "asked for by name; countersign is now on the critical path"; **Kokomi Bake-Kurage** (nowhere — new) — "render the summon entity (art exists: `Bake-Kurage Summon` 420×720) and preview the pulse's damage before end of turn. Gates re-asking Q1/Q4 at all"; **Klee bomb variety** — "bombs become varied effects, not only delayed damage — rework-scoped, not UI-scoped"; **burst visibility (all seats)** (nowhere — new) — "off-seat bursts are invisible inside the same end-of-turn noise; whatever the pass does for summons should carry burst attribution too". "Sprint-shaped with two [USER] touchpoints (R89 countersign; Klee rework is design)." Sequenced **ahead of** the corpse-detonation check and most of the Kokomi protocol, "because those need a legible end of turn to be answerable" — QUEUE `S4-G14`/`OT-1` is blocked on it | `git show pre-simplification-2026-08-06:docs/archive/playtest4-triage-2026-08-04.md` §N1, reached via the retired backlog §4 (`git show pre-simplification-2026-08-06:docs/archive/backlog-2026-07-29.md`); refiled 2026-08-08 (R136); dropped at the simplification |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-41` | Refactors, only if budget remains (big, safe, boring): `run_one` 518-line split; codegen driver unification (F3); telemetry-module template dedupe; `exp_*` script archive move; `apply_upgrade` op-coverage guard | eng-backlog §7 |
| `EB-48` | Two Furina experiment scripts read the DELETED fanfare constants and now die on import-time attribute access: `tier05/exp_furina_strength.py:476-477,503,631-632,733` and `tier05/exp_furina_parity_trace.py:125` reference `C.FANFARE_FLOOR_PER_POWER(_RARE)`, deleted by the 2026-07-28 Fanfare rework (`tier0/constants.py:248-256` records the deletion) — `AttributeError` on today's constants, and the S6 cell's thesis describes the deleted invisible-rule world. Fix or move to `tools/archive/` before any `S4-G7` re-measure runs into them | staleness audit 2026-08-07 |
| `EB-49` | The in-process rework-sim idiom (`tools/archive/klee_rework_sim.py`) silently measures the shipped card in three ways: (a) `loader._card_prototype` is lru_cached, so patching `_card_index()[cid].effects` after any run leaves every upgraded `<id>+` prototype holding the shipped effects — the patch must be followed by `loader._card_prototype.cache_clear()`; (b) `model.run_many(jobs>1)` crosses a `ProcessPoolExecutor` boundary the patch does not survive, so a parallel rework sim A/Bs the shipped card against itself — rework sims must run `jobs=1`; (c) `exp_fanfare_compensation` C3 keys fire-rate on the base id only, excluding upgraded copies. Fix the archive script or promote a hardened `rework_sim` helper; found 2026-08-08 during the S4-G9r measurement | S4-G9r measurement session |
| `EB-51` | Read the top-5 findings of the two severity-ordered audit ledgers (`docs/archive/lore-fidelity-audit-2026-08-05.md`, `docs/archive/instrument-redteam-2026-08-05.md`, both at the tag; both self-declare zero design authority) and triage per the three-way audit rule — confirmed defect → BACKLOG, design/taste call → QUEUE, else nowhere. `O-1` is already ruled and shipped (2026-08-06 sitting); the reactions-corpus countersign stays [USER]'s (QUEUE "N + O countersign" row) | user-queue §4; routed 2026-08-08 (R136) |
| `EB-55` | Draft the `EB-26` candidate card — a Kokomi uncommon lesser ward (P4 prevention-on-curve) — for [USER] ratification; EB-22's draft-then-ratify split is the model | eng-backlog; split from QUEUE EB-26 2026-08-08 (R136) |

## tests — pins & filed-not-fixed

| ID | Item | Provenance |
|---|---|---|
| `EB-11` | Understudy Defect 13 — `no_action` on a state with no `state_type`; **FILED, NOT FIXED** (next traversal pass) | eng-backlog §2 |
| `EB-12` | Understudy Defect 14 — `bridge_unreachable` by timeout with the process alive; one observation, no reproduction; **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-13` | Understudy Defect 15 — `no_progress`, the map↔rest_site bounce (seed `43MLG7MG9L`); **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-15` | The seed's `lobby` route never fired in three live runs; the lobby arm is retained and reports itself — nobody should read "two routes work" out of it | eng-backlog §2 |

## art — production work (the *picks* are [USER]'s in QUEUE; these are not)

| ID | Item | Provenance |
|---|---|---|
| `EB-36` | Three shipped cards render the BETA placeholder: `spotlight_center_stage`, `spotlight_guest_cast`, `confiscated` — zero `art/plan.tsv` rows. **Blind spot CLOSED** (2026-08-07): `art_coverage.py` billed from the sheets alone, so a C#-only card (the two selector halves) or a rarity:status token (`confiscated`) was neither COVERED, MISSING nor STALE — "art bill 0 missing" was true and wrong. The tool now takes a second universe from the portrait keys the shipped mod actually requests and bills the remainder; the three read as MISSING (271 covered / 274 expected) and `--strict` is honestly red until they land. **Remains: the hunt + the pick** (picks are [USER]'s — QUEUE art-debt row) | eng-backlog §6; missed-requirements §4.1 |
| `EB-37` | The character-icon `_outline` asset was never produced — `Klee.cs:146`,`Furina.cs:84`,`Kokomi.cs:134` all return the fill `char_icon.png`; no outline row in plan/SOURCES | eng-backlog §6; missed-requirements §4.2 |
| `EB-38` | Animation Track F3 + the sprint-1 polish deferral — rest/merchant gentle idles both characters; in-combat layer approved and frozen but no polish sprint opened | eng-backlog §6; missed-requirements §4.5 |
| `EB-39` | `no_holding_back` still uses the `Klee Multi Wish` source L6 flagged as trimming 76% of the image | eng-backlog §6; missed-requirements §4.6 |
| `EB-40` | Furina's energy counter: `Furina.cs:97` still points at `ironclad_energy_counter.tscn`; `energy_icon_74/22` have no plan rows | eng-backlog §6; furina-art-pass-requirements §8 |
| `EB-42` | Skeleton2D live-combat seating probe — the spike is DONE and PROMISING (`d69b7a0`: Kokomi rig packs, converts, and skins from computed weights, 5 bones / 4 Polygon2D / 112 weights, full pack-mount chain headless); the one untestable-offline link is seating as creature Visuals in live combat (RenderingServer RID reads invalid under the headless renderer) — one M-Q3-style probe, apparatus in `tools/skeleton2d_spike/`. The $379 Spine-licence reconsider → QUEUE `EB-42q` | eng-backlog §6; R118 |
| `EB-52` | Stage the outstanding running-game captures: (a) the fourth Fanfare evidence shape — a Power being played and the Fanfare floor rising because of it, staged on one of the three RARE `gain_fanfare_floor` Powers (`unheard_confession`, `the_sea_is_my_stage`, `rapturous_applause`), graded pass/fail against the written spec like the first three shapes (`review/active/red-pen-2026-07-26.md` Part 3) — escalate to QUEUE only if the capture shows something the spec doesn't decide; (b) the `AS2-D5` salon capture; (c) the `AS2-B5` motion-pass capture — (b) and (c) feed the QUEUE `S4-G17` eyes-on | S4-G16 + S4-G17 ops legs, routed 2026-08-08 (R136) |
| `EB-54` | Art production runs whose *picks* wait in the QUEUE Art-debt row: the `grand_gala` re-hunt; the `AS2-E2` icon re-hunt (4 of 7); the three `S4-G12` re-hunt candidates' contact sheet; the four missing Kokomi portraits; the `curtain_cue` wordmark; the `breathless` mood; A7 + six Curtain Call power sigils. Each run lands a contact sheet / candidate set for [USER] | user-queue §8; art-ops legs routed 2026-08-08 (R136) |
